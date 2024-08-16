import React, { useEffect, useState } from 'react';

function Dashboard() {
    const [handouts, setHandouts] = useState([]);
    const [progress, setProgress] = useState({});

    useEffect(() => {
        // Fetch handouts
        fetch('/api/handouts')
            .then(response => response.json())
            .then(data => setHandouts(data));

        // Fetch user progress if logged in
        fetch('/api/progress')
            .then(response => response.json())
            .then(data => setProgress(data));
    }, []);

    const handleCheckboxChange = (handoutId) => {
        const isCompleted = !progress[handoutId];
        setProgress(prev => ({ ...prev, [handoutId]: isCompleted }));

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
