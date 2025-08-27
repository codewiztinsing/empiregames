import React, { useState, useEffect } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import { Plus, Edit, Trash2, Save, X } from 'lucide-react';

function ContactInfo() {
  const [contacts, setContacts] = useState([
    {
      id: 1,
      type: 'Telegram',
      value: '@telegram',
      description: 'Official Telegram Channel',
      status: true
    }
  ]);
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({
    type: '',
    value: '',
    description: '',
    status: true
  });
  const [showAddForm, setShowAddForm] = useState(false);
  const [newContact, setNewContact] = useState({
    type: '',
    value: '',
    description: '',
    status: true
  });

  const handleEdit = (contact) => {
    setEditingId(contact.id);
    setEditForm({
      type: contact.type,
      value: contact.value,
      description: contact.description,
      status: contact.status
    });
  };

  const handleSaveEdit = () => {
    setContacts(contacts.map(contact => 
      contact.id === editingId 
        ? { ...contact, ...editForm }
        : contact
    ));
    setEditingId(null);
    setEditForm({ type: '', value: '', description: '', status: true });
    toast.success('Contact updated successfully');
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditForm({ type: '', value: '', description: '', status: true });
  };

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this contact?')) {
      setContacts(contacts.filter(contact => contact.id !== id));
      toast.success('Contact deleted successfully');
    }
  };

  const handleAddContact = () => {
    if (!newContact.type || !newContact.value) {
      toast.error('Please fill in required fields');
      return;
    }

    const newId = Math.max(...contacts.map(c => c.id), 0) + 1;
    setContacts([...contacts, { ...newContact, id: newId }]);
    setNewContact({ type: '', value: '', description: '', status: true });
    setShowAddForm(false);
    toast.success('Contact added successfully');
  };

  const toggleStatus = (id) => {
    setContacts(contacts.map(contact =>
      contact.id === id
        ? { ...contact, status: !contact.status }
        : contact
    ));
  };

  return (
    <>
      <div className='h-screen w-full overflow-y-auto'>
        <Toaster position="top-right" reverseOrder={false} />
        
        <div className="min-h-screen bg-gray-900 p-6 w-full">
          <div className="w-full">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-3xl font-bold text-white mb-2">Contact Information Management</h1>
                <p className="text-gray-400">Manage contact details and communication channels</p>
              </div>
              <button
                onClick={() => setShowAddForm(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg flex items-center gap-2 transition-colors"
              >
                <Plus className="w-5 h-5" />
                Add New Contact
              </button>
            </div>

            {/* Add Contact Form */}
            {showAddForm && (
              <div className="bg-gray-800 p-6 rounded-xl mb-6">
                <h3 className="text-xl font-semibold text-white mb-4">Add New Contact</h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Type</label>
                    <input
                      type="text"
                      value={newContact.type}
                      onChange={(e) => setNewContact({...newContact, type: e.target.value})}
                      className="w-full bg-gray-700 text-white px-3 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                      placeholder="e.g., Telegram, WhatsApp"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Value</label>
                    <input
                      type="text"
                      value={newContact.value}
                      onChange={(e) => setNewContact({...newContact, value: e.target.value})}
                      className="w-full bg-gray-700 text-white px-3 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                      placeholder="@username or contact details"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
                    <input
                      type="text"
                      value={newContact.description}
                      onChange={(e) => setNewContact({...newContact, description: e.target.value})}
                      className="w-full bg-gray-700 text-white px-3 py-2 rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
                      placeholder="Brief description"
                    />
                  </div>
                  <div className="flex items-end gap-2">
                    <button
                      onClick={handleAddContact}
                      className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
                    >
                      <Save className="w-4 h-4" />
                      Add
                    </button>
                    <button
                      onClick={() => {
                        setShowAddForm(false);
                        setNewContact({ type: '', value: '', description: '', status: true });
                      }}
                      className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
                    >
                      <X className="w-4 h-4" />
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Contact Table */}
            <div className="bg-gray-800 rounded-xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-700">
                    <tr>
                      <th className="text-left p-4 text-gray-300 font-medium">Type</th>
                      <th className="text-left p-4 text-gray-300 font-medium">Value</th>
                      <th className="text-left p-4 text-gray-300 font-medium">Description</th>
                      <th className="text-left p-4 text-gray-300 font-medium">Status</th>
                      <th className="text-left p-4 text-gray-300 font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {contacts.map((contact) => (
                      <tr key={contact.id} className="border-b border-gray-700 hover:bg-gray-750">
                        <td className="p-4">
                          {editingId === contact.id ? (
                            <input
                              type="text"
                              value={editForm.type}
                              onChange={(e) => setEditForm({...editForm, type: e.target.value})}
                              className="w-full bg-gray-700 text-white px-3 py-1 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
                            />
                          ) : (
                            <span className="text-white font-medium">{contact.type}</span>
                          )}
                        </td>
                        <td className="p-4">
                          {editingId === contact.id ? (
                            <input
                              type="text"
                              value={editForm.value}
                              onChange={(e) => setEditForm({...editForm, value: e.target.value})}
                              className="w-full bg-gray-700 text-white px-3 py-1 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
                            />
                          ) : (
                            <span className="text-blue-400">{contact.value}</span>
                          )}
                        </td>
                        <td className="p-4">
                          {editingId === contact.id ? (
                            <input
                              type="text"
                              value={editForm.description}
                              onChange={(e) => setEditForm({...editForm, description: e.target.value})}
                              className="w-full bg-gray-700 text-white px-3 py-1 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
                            />
                          ) : (
                            <span className="text-gray-300">{contact.description}</span>
                          )}
                        </td>
                        <td className="p-4">
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input
                              type="checkbox"
                              checked={editingId === contact.id ? editForm.status : contact.status}
                              onChange={() => editingId === contact.id 
                                ? setEditForm({...editForm, status: !editForm.status})
                                : toggleStatus(contact.id)
                              }
                              className="sr-only peer"
                            />
                            <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                          </label>
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-2">
                            {editingId === contact.id ? (
                              <>
                                <button
                                  onClick={handleSaveEdit}
                                  className="bg-green-600 hover:bg-green-700 text-white p-2 rounded-lg transition-colors"
                                >
                                  <Save className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={handleCancelEdit}
                                  className="bg-gray-600 hover:bg-gray-700 text-white p-2 rounded-lg transition-colors"
                                >
                                  <X className="w-4 h-4" />
                                </button>
                              </>
                            ) : (
                              <>
                                <button
                                  onClick={() => handleEdit(contact)}
                                  className="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-lg transition-colors"
                                >
                                  <Edit className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => handleDelete(contact.id)}
                                  className="bg-red-600 hover:bg-red-700 text-white p-2 rounded-lg transition-colors"
                                >
                                  <Trash2 className="w-4 h-4" />
                                </button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {contacts.length === 0 && (
                  <div className="text-center py-12">
                    <p className="text-gray-400">No contact information found.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default ContactInfo;
