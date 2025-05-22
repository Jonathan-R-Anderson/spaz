#!/bin/bash
set -e

export DEBIAN_FRONTEND=noninteractive

echo "🔥 Initializing KDC for realm: $REALM"
echo $REALM > /etc/krb5kdc/kdc.conf

echo -e "*/admin@$REALM *" > /etc/krb5kdc/kadm5.acl

krb5_newrealm

echo "🧪 Creating service principal: $PRINCIPAL"
kadmin.local -q "addprinc -randkey $PRINCIPAL"
kadmin.local -q "ktadd -k $KEYTAB $PRINCIPAL"

echo "✅ Keytab generated at $KEYTAB"

tail -f /dev/null  # Keep container running
