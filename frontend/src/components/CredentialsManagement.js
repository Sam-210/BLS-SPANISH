import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const CredentialsManagement = () => {
  const [credentials, setCredentials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingCredential, setEditingCredential] = useState(null);
  const [testing, setTesting] = useState(false);
  const [formData, setFormData] = useState({
    credential_name: '',
    email: '',
    password: '',
    is_primary: false,
    notes: ''
  });

  useEffect(() => {
    fetchCredentials();
  }, []);

  const fetchCredentials = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/credentials`);
      setCredentials(response.data.credentials);
      setError('');
    } catch (err) {
      setError('Failed to fetch credentials');
      console.error('Error fetching credentials:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const resetForm = () => {
    setFormData({
      credential_name: '',
      email: '',
      password: '',
      is_primary: false,
      notes: ''
    });
    setEditingCredential(null);
    setShowForm(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingCredential) {
        // Update existing credential
        await axios.put(`${API}/credentials/${editingCredential.id}`, formData);
        setSuccess('Credential updated successfully');
      } else {
        // Create new credential
        await axios.post(`${API}/credentials`, formData);
        setSuccess('Credential created successfully');
      }
      
      resetForm();
      fetchCredentials();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save credential');
      setTimeout(() => setError(''), 5000);
    }
  };

  const handleEdit = (credential) => {
    setFormData({
      credential_name: credential.credential_name,
      email: credential.email,
      password: credential.password,
      is_primary: credential.is_primary,
      notes: credential.notes || ''
    });
    setEditingCredential(credential);
    setShowForm(true);
  };

  const handleDelete = async (credentialId) => {
    if (!window.confirm('Are you sure you want to delete this credential?')) {
      return;
    }

    try {
      await axios.delete(`${API}/credentials/${credentialId}`);
      setSuccess('Credential deleted successfully');
      fetchCredentials();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete credential');
      setTimeout(() => setError(''), 5000);
    }
  };

  const setPrimaryCredential = async (credentialId) => {
    try {
      await axios.post(`${API}/credentials/${credentialId}/set-primary`);
      setSuccess('Primary credential updated successfully');
      fetchCredentials();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to set primary credential');
      setTimeout(() => setError(''), 5000);
    }
  };

  const testCredential = async (credentialId) => {
    try {
      setTesting(true);
      const response = await axios.post(`${API}/credentials/${credentialId}/test`);
      
      if (response.data.success) {
        setSuccess(`Credential test successful! Response time: ${response.data.response_time_ms}ms`);
      } else {
        setError(`Credential test failed: ${response.data.message}`);
      }
      
      fetchCredentials(); // Refresh to update statistics
      setTimeout(() => {
        setSuccess('');
        setError('');
      }, 5000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to test credential');
      setTimeout(() => setError(''), 5000);
    } finally {
      setTesting(false);
    }
  };

  const toggleCredentialStatus = async (credential) => {
    try {
      await axios.put(`${API}/credentials/${credential.id}`, {
        is_active: !credential.is_active
      });
      setSuccess(`Credential ${credential.is_active ? 'deactivated' : 'activated'} successfully`);
      fetchCredentials();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update credential status');
      setTimeout(() => setError(''), 5000);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="bg-white shadow-lg rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Login Credentials</h2>
              <p className="text-sm text-gray-600 mt-1">
                Manage BLS website login credentials for automation
              </p>
            </div>
            <button
              onClick={() => setShowForm(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium transition-colors"
            >
              Add New Credential
            </button>
          </div>
        </div>

        {error && (
          <div className="mx-6 mt-4 bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded">
            {error}
          </div>
        )}

        {success && (
          <div className="mx-6 mt-4 bg-green-100 border-l-4 border-green-500 text-green-700 p-4 rounded">
            {success}
          </div>
        )}

        {/* Form Modal */}
        {showForm && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-11/12 max-w-md shadow-lg rounded-md bg-white">
              <div className="mt-3">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  {editingCredential ? 'Edit Credential' : 'Add New Credential'}
                </h3>
                
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Credential Name *
                    </label>
                    <input
                      type="text"
                      name="credential_name"
                      value={formData.credential_name}
                      onChange={handleInputChange}
                      required
                      placeholder="e.g., Main Account, Backup Account"
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">Friendly name to identify this credential</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Email *
                    </label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                      placeholder="your.email@example.com"
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Password *
                    </label>
                    <input
                      type="password"
                      name="password"
                      value={formData.password}
                      onChange={handleInputChange}
                      required
                      placeholder="Your BLS account password"
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      ⚠️ Passwords are stored securely but visible in this form
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Notes
                    </label>
                    <textarea
                      name="notes"
                      value={formData.notes}
                      onChange={handleInputChange}
                      rows={3}
                      placeholder="Additional notes about this credential..."
                      className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        name="is_primary"
                        checked={formData.is_primary}
                        onChange={handleInputChange}
                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700">
                        Set as primary credential (used for automation)
                      </span>
                    </label>
                  </div>

                  <div className="flex justify-end space-x-3 pt-4 border-t">
                    <button
                      type="button"
                      onClick={resetForm}
                      className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      {editingCredential ? 'Update' : 'Create'} Credential
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Credentials List */}
        <div className="px-6 py-4">
          {credentials.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-gray-500 text-lg">No credentials found</div>
              <p className="text-gray-400 text-sm mt-2">
                Add your first BLS login credential to get started
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Performance
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Last Used
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {credentials.map((credential) => (
                    <tr key={credential.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {credential.credential_name}
                            </div>
                            {credential.notes && (
                              <div className="text-sm text-gray-500 truncate max-w-xs">
                                {credential.notes}
                              </div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{credential.email}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-2">
                          {credential.is_primary && (
                            <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                              Primary
                            </span>
                          )}
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            credential.is_active 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {credential.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {credential.total_attempts > 0 ? (
                            <>
                              <div>Success: {(credential.success_rate * 100).toFixed(1)}%</div>
                              <div className="text-xs text-gray-500">
                                {credential.successful_attempts}/{credential.total_attempts} attempts
                              </div>
                            </>
                          ) : (
                            <div className="text-sm text-gray-500">No attempts yet</div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">
                          {credential.last_used 
                            ? new Date(credential.last_used).toLocaleDateString()
                            : 'Never'
                          }
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => testCredential(credential.id)}
                            disabled={testing}
                            className="text-indigo-600 hover:text-indigo-900 disabled:opacity-50"
                          >
                            {testing ? 'Testing...' : 'Test'}
                          </button>
                          <button
                            onClick={() => handleEdit(credential)}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            Edit
                          </button>
                          {!credential.is_primary && (
                            <button
                              onClick={() => setPrimaryCredential(credential.id)}
                              className="text-green-600 hover:text-green-900"
                            >
                              Set Primary
                            </button>
                          )}
                          <button
                            onClick={() => toggleCredentialStatus(credential)}
                            className={credential.is_active 
                              ? 'text-orange-600 hover:text-orange-900' 
                              : 'text-green-600 hover:text-green-900'
                            }
                          >
                            {credential.is_active ? 'Deactivate' : 'Activate'}
                          </button>
                          <button
                            onClick={() => handleDelete(credential.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CredentialsManagement;