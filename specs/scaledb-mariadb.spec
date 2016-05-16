%define __spec_install_pre /bin/true
 
Name:          scaledb-mariadb
Vendor:        ScaleDB, Inc. <info@scaledb.com>
Version:       16.04.01
Release:       10.1.13
BuildArch:     x86_64
Summary:       MariaDB Server optimized for ScaleDB Cluster and ScaleDB ONE 
License:       GPLv2
Group: 	       database
URL:           http://www.scaledb.com

%define install_path	/usr/local

Prefix:        /usr/local
Conflicts:     mariadb-server, mysql-server
Requires:      epel-release >= 7-5, jemalloc >= 3.5.1
AutoReqProv:   no



%description
MariaDB Server optimized for ScaleDB Cluster and ScaleDB ONE 

 

    
%pre
#!/bin/bash
#
# Copyright 2016 ScaleDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

set -e

SCALEDB_MARIADB_BASEDIR="/usr/local/scaledb-mariadb-16.04.01-10.1.13"
SCALEDB_MARIADB_LINK_BASEDIR="/usr/local/mysql"

echo                                                                                   >  /dev/tty
echo "MariaDB for ScaleDB Installation"                                                >  /dev/tty
echo                                                                                   >  /dev/tty
echo "This is a version of MariaDB Server customized to work with ScaleDB"             >  /dev/tty
echo -n "Please press <Enter> to continue with the installation or <Ctrl-C> to exit: " >  /dev/tty
read continue_inst  < /dev/tty

echo ""   >  /dev/tty

# Check if the mysql dir link is already set
if [ -L "${SCALEDB_MARIADB_LINK_BASEDIR}" -o -d "${SCALEDB_MARIADB_LINK_BASEDIR}" ]; then
	echo
	echo "${SCALEDB_MARIADB_LINK_BASEDIR} is already set. Remove the folder or link and run the installation again."
	exit 1
fi

# Check if the mysql utility link is already set
if [ -L "/usr/bin/mysql" -o -f "/usr/bin/mysql" ]; then
	echo
	echo "/usr/bin/mysql is already set. Remove the program or link and run the installation again."
	exit 1
fi

# Check if a my.cnf configuration file exists and rename it in order to not
# conflict with the scaledb configuration file
if [ -f "/etc/my.cnf" ]; then
	mv /etc/my.cnf /etc/my.cnf-pre_scaledb
	echo 
	echo "The configuration file /etc/my.cnf has been renamed /etc/my.cnf-pre_scaledb."

fi

# Check if a my.cnf.d configuration directory exists and rename it in order to not
# conflict with the scaledb configuration file
if [ -d "/etc/my.cnf.d" ]; then
	mv /etc/my.cnf.d /etc/my.cnf.d-pre_scaledb
	echo 
	echo "The configuration directory /etc/my.cnf.d has been renamed /etc/my.cnf.d-pre_scaledb."

fi

# Check if the mysql configuration dir exists and rename it in order to not
# conflict with the scaledb configuration file
if [ -f "/etc/mysql" ]; then
	mv /etc/mysql /etc/mysql-pre_scaledb
	echo 
	echo "The configuration folder /etc/mysql has been renamed /etc/mysql-pre_scaledb."

fi

# Check if the scaledb group exists and create it if it does not
if [ "`grep -c '^scaledb:' /etc/group`" = "0" ]; then


        groupadd scaledb > /dev/null
	if [ "$?" != "0" ]; then
		echo "Error creating the scaledb group."
		exit 1
	fi

fi

# Check if the scaledb user exists and create it if it does not
if [ "`grep -c '^scaledb:' /etc/passwd`" = "0" ]; then

	adduser -g scaledb --comment "ScaleDB" --shell /bin/bash scaledb > /dev/null

	# If the adduser has been OK, set the password
	if [ "$?" = "0" ]; then		
		echo scaledb | passwd scaledb --stdin  > /dev/null
		if [ "$?" != "0" ]; then
			echo "Error setting password for scaledb user."
			exit 1
		fi	
	else
		echo "Error creating the scaledb user."
		exit 1
	fi

fi


exit $?



%post
#!/bin/sh
#
# Copyright 2016 ScaleDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

set -e

SCALEDB_MARIADB_PACKAGE="scaledb-mariadb-16.04.01-10.1.13"
SCALEDB_MARIADB_PARENTDIR="/usr/local"
SCALEDB_MARIADB_BASEDIR="${SCALEDB_MARIADB_PARENTDIR}/${SCALEDB_MARIADB_PACKAGE}"
SCALEDB_MARIADB_LINK_BASEDIR="${SCALEDB_MARIADB_PARENTDIR}/mysql"

# Used to set the PATH for the scaledb user
newpath=""

echo "Setting the ScaleDB and MariaDB environment..."

# Set the Base dir
cd "${SCALEDB_MARIADB_PARENTDIR}"

# Set the mysql symbolic link
ln -s "${SCALEDB_MARIADB_BASEDIR}" "${SCALEDB_MARIADB_LINK_BASEDIR}"
if [ "$?" != "0" ]; then
	echo "Error setting the ${SCALEDB_MARIADB_LINK_BASEDIR} symbolic link."
	exit 1
fi

# Change the ownership of the installed files
chown -R scaledb:scaledb "${SCALEDB_MARIADB_BASEDIR}"
if [ "$?" != "0" ]; then
	echo "Error changing ownership of the MariaDB base directory."
	exit 1
fi

chown -R scaledb:scaledb "${SCALEDB_MARIADB_LINK_BASEDIR}"
if [ "$?" != "0" ]; then
	echo "Error changing ownership of the mysql symbolic link."
	exit 1
fi

# Link the MySQL Client utility
ln -s "${SCALEDB_MARIADB_BASEDIR}/bin/mysql" "/usr/bin/mysql"
if [ "$?" != "0" ]; then
	echo "Error creating the mysql utility link."
	exit 1
fi

# Retrieve the home directory path for the scaledb user
scaledb_home_dir=`grep "^scaledb" /etc/passwd | cut -d: -f6`

# Work only if .bash_profile exists
if [ -f "${scaledb_home_dir}/.bash_profile" ]; then

	# Setting the new path to ...mysql/bin for the scaledb user
	if  [ `grep -c "^\s*PATH=.*${SCALEDB_MARIADB_LINK_BASEDIR}/bin" "${scaledb_home_dir}/.bash_profile"` -eq 0 ]; then
		new_path="${SCALEDB_MARIADB_LINK_BASEDIR}/bin:"
	fi

	# Setting the new path to ...mysql/support-files for the scaledb user
	if  [ `grep -c "^\s*PATH=.*${SCALEDB_MARIADB_LINK_BASEDIR}/support-files" "${scaledb_home_dir}/.bash_profile"` -eq 0 ]; then
		new_path="${new_path}${SCALEDB_MARIADB_LINK_BASEDIR}/support-files:"
	fi

	# Adding the rows to .bash_profile
	if [ "${new_path}" != "" ]; then
		echo  >> "${scaledb_home_dir}/.bash_profile"
		echo "# Added by the ScaleDB MariaDB package installer" >> "${scaledb_home_dir}/.bash_profile"
		echo "PATH=\"${new_path}\${PATH}\"" >> "${scaledb_home_dir}/.bash_profile"
		echo  >> "${scaledb_home_dir}/.bash_profile"
	fi

	# Adding the mysql alias to enable comments and warnings
	echo "alias mysql='mysql --comments --show-warnings'" >> "${scaledb_home_dir}/.bash_profile"
	echo  >> "${scaledb_home_dir}/.bash_profile"

fi

echo ""
echo "MariaDB for ScaleDB installation completed."
echo "You can control the Database node using the scaledb user. The default password is scaledb."
echo ""

exit $?


 
%preun 
#!/bin/sh
#
# Copyright 2016 ScaleDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

set -e

SCALEDB_MARIADB_PACKAGE="scaledb-mariadb-16.04.01-10.1.13"
SCALEDB_MARIADB_PARENTDIR="/usr/local"
SCALEDB_MARIADB_BASEDIR="${SCALEDB_MARIADB_PARENTDIR}/${SCALEDB_MARIADB_PACKAGE}"
SCALEDB_MARIADB_LINK_BASEDIR="${SCALEDB_MARIADB_PARENTDIR}/mysql"

# Stop the server if it is running
if [ `"${SCALEDB_MARIADB_BASEDIR}/support-files/mysql.server" status | tail -1 | grep -c "MySQL running"` -eq 1 ]
then
	"${SCALEDB_MARIADB_BASEDIR}/support-files/mysql.server" stop
fi


# Remove the Base dir link
if [ -L "${SCALEDB_MARIADB_LINK_BASEDIR}" ]
then
	rm ${SCALEDB_MARIADB_LINK_BASEDIR}
fi

# Remove the MySQL Client utility link
if [ -L "/usr/bin/mysql" ]
then
	rm /usr/bin/mysql
fi



exit $?
 
 
%postun
#!/bin/sh
#
# Copyright 2016 ScaleDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

set -e

SCALEDB_MARIADB_PACKAGE="scaledb-mariadb-16.04.01-10.1.13"
SCALEDB_MARIADB_PARENTDIR="/usr/local"
SCALEDB_MARIADB_BASEDIR="${SCALEDB_MARIADB_PARENTDIR}/${SCALEDB_MARIADB_PACKAGE}"
SCALEDB_MARIADB_LINK_BASEDIR="${SCALEDB_MARIADB_PARENTDIR}/mysql"


# Remove the MariaDB directory, if it is in the usual position
if [ -d "${SCALEDB_MARIADB_BASEDIR}" ]
then
	rm -rf ${SCALEDB_MARIADB_BASEDIR}
fi


if [ -f "/etc/my.cnf-pre_scaledb" ]
then
	mv /etc/my.cnf-pre_scaledb /etc/my.cnf
fi

if [ -d "/etc/my.cnf.d-pre_scaledb" ]
then
	mv /etc/my.cnf.d-pre_scaledb /etc/my.cnf.d
fi


if [ -f "/etc/mysql-pre_scaledb" ]
then
	mv /etc/mysql-pre_scaledb /etc/mysql
fi


exit $?



%files 
%{install_path}/*

 
