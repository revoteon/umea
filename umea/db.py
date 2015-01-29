import ldap

class Database:
    # impose required parameters!
    def __init__(self, **kwargs):
        self.adaptor = kwargs.get('adaptor')
        self.host = kwargs.get('host')
        self.port = kwargs.get('port') 
        self.user = kwargs.get('user')
        self.password = kwargs.get('password')
        self.secure = kwargs.get('secure', False)
        self.connection = None

    def _initialize(self):
        ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
        self.connection = ldap.ldapobject.ReconnectLDAPObject(self.uri(), retry_max=3)

        if self.secure:
            self.connection.set_option(ldap.OPT_REFERRALS, 0)
            self.connection.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            self.connection.set_option(ldap.OPT_X_TLS,ldap.OPT_X_TLS_DEMAND)
            self.connection.set_option( ldap.OPT_X_TLS_DEMAND, True )

        self.connection.bind_s(who=self.user, cred=self.password)


    def cursor(self):
        if not self.connection:
            self._initialize()
        return self.connection

    def search(self, params):
        return self.cursor().search_ext_s(*(params))

    def close(self):
        if self.connection:
            self.connection.unbind_s()
            self.connection = None

    def scheme(self):
        return 'ldaps' if self.secure else 'ldap'

    def uri(self):
        uri_format = "%(scheme)s://%(host)s:%(port)s/"
        return uri_format % {"scheme": self.scheme(), "host": self.host, "port": self.port}


class ActiveDirectory(Database):
    def search(self, params):
        entries = list()
        paged_result_control_type = ldap.controls.SimplePagedResultsControl.controlType
        paged_control = ldap.controls.SimplePagedResultsControl(True, size=1000, cookie='')
        message_id = self.cursor().search_ext(*(params), serverctrls=[paged_control])
        while True:
            _, results, _, result_controls = self.cursor().result3(message_id)
            entries.extend(results)
            paged_controls = [control for control in result_controls if control.controlType == paged_result_control_type]
            if paged_controls:
                if paged_controls[0].cookie:
                    paged_control.cookie = paged_controls[0].cookie
                    message_id = self.cursor().search_ext(*(params), serverctrls=[paged_control])
                else:
                    break
        return self._post_process(entries)

    def _post_process(self, entries):
        for i in xrange(len(entries)):
            dn, entry = entries[i]
            attributes = entry.keys()
            for attr in attributes:
                if ';range=' in attr:
                    attr_real_name, _ = attr.split(';') 
                    attr_all_values = self._fetch_range_values(dn, attr)
                    del entry[attr]
                    entry[attr_real_name] = attr_all_values 
        return entries


    def _fetch_range_values(self, dn, range_attr):
        values_list = list()
        while True:
            result = self.cursor().search_s(dn, ldap.SCOPE_BASE, attrlist=[range_attr])
            dn, entry = result[0]
            ret_attr = entry.keys()[0]
            ret_values = entry[ret_attr]
            values_list.extend(ret_values)
            if ret_attr.endswith("-*"):
                break

            real_attr, range_key = ret_attr.split(';')
            _, bounds = range_key.split('=')
            lower_bound, upper_bound = bounds.split('-')
            lower_bound = int(lower_bound)
            upper_bound = int(upper_bound)

            range_step = upper_bound - lower_bound + 1
            new_lower_bound = upper_bound + 1
            new_upper_bound = upper_bound + range_step

            range_attr = "%s;range=%d-%d" % (real_attr, new_lower_bound, new_upper_bound) 

        return values_list



class OracleDSEE(Database):
    pass
