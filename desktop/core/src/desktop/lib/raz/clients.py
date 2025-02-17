# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from requests_kerberos import HTTPKerberosAuth

from desktop.conf import RAZ
from desktop.lib.raz.ranger.clients.ranger_raz_adls import RangerRazAdls
from desktop.lib.raz.ranger.clients.ranger_raz_s3 import RangerRazS3


LOG = logging.getLogger(__name__)


class S3RazClient():

  def __init__(self, **kwargs):
    if RAZ.API_AUTHENTICATION.get() == 'kerberos':
      auth = HTTPKerberosAuth()
    else:
      auth = None

    self.ranger = RangerRazS3(RAZ.API_URL.get(), auth)

  def get_url(self, bucket=None, path=None, perm='read'):
    # No GET/POST spec?
    # e.g. get_url('<storage_account?>', '<bucket>', '<relative_path>', 'read')
    return self.ranger.get_dsas_token(bucket, path, perm)


class AdlsRazClient():

  def __init__(self):
    if RAZ.API_AUTHENTICATION.get() == 'kerberos':
      auth = HTTPKerberosAuth()
    else:
      auth = None

    self.ranger = RangerRazAdls(RAZ.API_URL.get(), auth)

  def get_url(self, storage_account, container, relative_path, perm='read'):
    # e.g. get_url('<storage_account>', '<container>', '<relative_path>', 'read')
    return self.ranger.get_dsas_token(storage_account, container, relative_path, perm)
