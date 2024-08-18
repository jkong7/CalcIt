import React, { useEffect, useState } from 'react';

// ------------------ Dashboard Component ------------------

function Dashboard() {
    // ------------------ State Management ------------------
    
    const [handouts, setHandouts] = useState([]); // Stores the list of handouts
    const [progress, setProgress] = useState({}); // Tracks user's progress on handouts

    // ------------------ useEffect: Data Fetching ------------------
    
    useEffect(() => {
        // Fetch handouts from the API
        fetch('/api/handouts')
            .then(response => response.json())
            .then(data => setHandouts(data));

        // Fetch user progress if logged in
        fetch('/api/progress')
            .then(response => response.json())
            .then(data => setProgress(data));
    }, []); 

    // ------------------ Event Handlers ------------------
    
    // Handles the change of the checkbox state
    const handleCheckboxChange = (handoutId) => {
        const isCompleted = !progress[handoutId]; // Toggle the completion state
        setProgress(prev => ({ ...prev, [handoutId]: isCompleted })); // Update local state

        // Send updated progress to the server
        fetch('/update_progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'handout_id': handoutId,
                'is_completed': isCompleted
            })
        });
    };

    // ------------------ JSX Rendering ------------------
    
    return (
        <div className="dashboard">
            {handouts.map(handout => (
                <div key={handout.id} className="handout-item">
                    <input
                        type="checkbox"
                        checked={!!progress[handout.id]} 
                        onChange={() => handleCheckboxChange(handout.id)}
                    />
                    <span>{handout.title}</span>
                </div>
            ))}
        </div>
    );
}

export default Dashboard;
