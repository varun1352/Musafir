import React from 'react';

const popupContainerStyle = {
  position: 'fixed',
  top: 0,
  left: 0,
  width: '100vw',
  height: '100vh',
  backgroundColor: 'rgba(0, 0, 0, 0.6)',
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  zIndex: 1000,
  animation: 'fadeIn 0.3s ease-in-out',
};

const popupContentStyle = {
  background: '#fff',
  borderRadius: '10px',
  padding: '20px',
  width: '320px',
  maxHeight: '80vh',
  overflowY: 'auto',
  boxShadow: '0 4px 20px rgba(0,0,0,0.3)',
  position: 'relative',
};

const closeButtonStyle = {
  position: 'absolute',
  top: '10px',
  right: '10px',
  background: 'transparent',
  border: 'none',
  fontSize: '24px',
  cursor: 'pointer',
};

const userCardStyle = {
  marginBottom: '15px',
  padding: '10px',
  border: '1px solid #ddd',
  borderRadius: '5px',
};

const userNameStyle = {
  fontSize: '16px',
  fontWeight: 'bold',
  marginBottom: '5px',
};

const timeSlotStyle = {
  fontSize: '14px',
  color: '#555',
};

export default function NodePopup({ node, onClose }) {
  return (
    <div style={popupContainerStyle}>
      <div style={popupContentStyle}>
        <button style={closeButtonStyle} onClick={onClose}>
          &times;
        </button>
        <h2 style={{ marginTop: 0 }}>{node.name}</h2>
        <p style={{ fontWeight: 'bold' }}>Users at this location:</p>
        {node.users.map((user, index) => (
          <div key={index} style={userCardStyle}>
            <div style={userNameStyle}>{user.name}</div>
            <div style={timeSlotStyle}>
              {user.timeSlots.map((slot, i) => (
                <div key={i}>{slot}</div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
