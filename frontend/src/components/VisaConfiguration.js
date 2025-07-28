import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function VisaConfiguration({ onConfigurationChange, initialConfig }) {
  const [visaTypes, setVisaTypes] = useState({});
  const [appointmentTypes, setAppointmentTypes] = useState([]);
  const [selectedVisaType, setSelectedVisaType] = useState('Tourist Visa');
  const [selectedVisaSubtype, setSelectedVisaSubtype] = useState('Short Stay');
  const [selectedAppointmentType, setSelectedAppointmentType] = useState('Individual');
  const [numberOfMembers, setNumberOfMembers] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchVisaTypes();
  }, []);

  useEffect(() => {
    if (initialConfig) {
      setSelectedVisaType(initialConfig.visa_type || 'Tourist Visa');
      setSelectedVisaSubtype(initialConfig.visa_subtype || 'Short Stay');
      setSelectedAppointmentType(initialConfig.appointment_type || 'Individual');
      setNumberOfMembers(initialConfig.number_of_members || 1);
    }
  }, [initialConfig]);

  const fetchVisaTypes = async () => {
    try {
      const response = await axios.get(`${API}/visa-types`);
      setVisaTypes(response.data.visa_types);
      setAppointmentTypes(response.data.appointment_types);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch visa types:', error);
      setLoading(false);
    }
  };

  const handleVisaTypeChange = (visaType) => {
    setSelectedVisaType(visaType);
    // Set first available subtype as default
    const availableSubtypes = visaTypes[visaType] || [];
    if (availableSubtypes.length > 0) {
      setSelectedVisaSubtype(availableSubtypes[0]);
    }
    notifyConfigChange(visaType, availableSubtypes[0], selectedAppointmentType, numberOfMembers);
  };

  const handleVisaSubtypeChange = (subtype) => {
    setSelectedVisaSubtype(subtype);
    notifyConfigChange(selectedVisaType, subtype, selectedAppointmentType, numberOfMembers);
  };

  const handleAppointmentTypeChange = (appointmentType) => {
    setSelectedAppointmentType(appointmentType);
    // Reset number of members if switching to Individual
    const members = appointmentType === 'Individual' ? 1 : numberOfMembers;
    setNumberOfMembers(members);
    notifyConfigChange(selectedVisaType, selectedVisaSubtype, appointmentType, members);
  };

  const handleNumberOfMembersChange = (members) => {
    setNumberOfMembers(members);
    notifyConfigChange(selectedVisaType, selectedVisaSubtype, selectedAppointmentType, members);
  };

  const notifyConfigChange = (visaType, visaSubtype, appointmentType, members) => {
    if (onConfigurationChange) {
      onConfigurationChange({
        visa_type: visaType,
        visa_subtype: visaSubtype,
        appointment_type: appointmentType,
        number_of_members: members
      });
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold mb-4 text-gray-800">🎯 Visa Configuration</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Visa Type Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Visa Type *
          </label>
          <select
            value={selectedVisaType}
            onChange={(e) => handleVisaTypeChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {Object.keys(visaTypes).map((visaType) => (
              <option key={visaType} value={visaType}>
                {visaType}
              </option>
            ))}
          </select>
        </div>

        {/* Visa Subtype Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Visa Sub Type *
          </label>
          <select
            value={selectedVisaSubtype}
            onChange={(e) => handleVisaSubtypeChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {(visaTypes[selectedVisaType] || []).map((subtype) => (
              <option key={subtype} value={subtype}>
                {subtype}
              </option>
            ))}
          </select>
        </div>

        {/* Appointment Type Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Appointment For *
          </label>
          <select
            value={selectedAppointmentType}
            onChange={(e) => handleAppointmentTypeChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {appointmentTypes.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>

        {/* Number of Members (only show for Family) */}
        {selectedAppointmentType === 'Family' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Number Of Members *
            </label>
            <input
              type="number"
              min="1"
              max="10"
              value={numberOfMembers}
              onChange={(e) => handleNumberOfMembersChange(parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        )}
      </div>

      {/* Configuration Summary */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="text-sm font-medium text-blue-800 mb-2">📋 Current Configuration:</h4>
        <div className="text-sm text-blue-700 space-y-1">
          <div><span className="font-medium">Visa Type:</span> {selectedVisaType}</div>
          <div><span className="font-medium">Sub Type:</span> {selectedVisaSubtype}</div>
          <div><span className="font-medium">Appointment:</span> {selectedAppointmentType}</div>
          {selectedAppointmentType === 'Family' && (
            <div><span className="font-medium">Members:</span> {numberOfMembers}</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default VisaConfiguration;