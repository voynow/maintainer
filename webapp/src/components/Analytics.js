import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAppContext } from '../AppContext';

const Analytics = () => {
    const { email } = useAppContext();
    const [metrics, setMetrics] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchMetrics = async () => {
        try {
            setIsLoading(true);
            const response = await axios.get("/get_metrics", {
                params: { user_email: email, project_name: "YourProjectName" },
                headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
            });

            if (response.status === 200) {
                setMetrics(response.data);
            }
        } catch (err) {
            if (err.response?.status === 404) {
                setError("Metrics not found");
            } else {
                setError("An error occurred");
            }
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (email) {
            fetchMetrics();
        }
    }, [email]);

    return (
        <div>
            {isLoading ? (
                <p>Loading...</p>
            ) : error ? (
                <p>{error}</p>
            ) : (
                <table className="min-w-full divide-y divide-gray-200">
                    <thead>
                        <tr>
                            <th>File Path</th>
                            <th>Readability</th>
                            <th>Design Quality</th>
                            <th>Testability</th>
                            <th>Consistency</th>
                            <th>Error Handling</th>
                        </tr>
                    </thead>
                    <tbody>
                        {metrics.map((metric, index) => (
                            <tr key={index}>
                                <td>{metric.file_path}</td>
                                <td>{metric.readability}</td>
                                <td>{metric.design_quality}</td>
                                <td>{metric.testability}</td>
                                <td>{metric.consistency}</td>
                                <td>{metric.debug_error_handling}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default Analytics;
