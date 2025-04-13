import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { Send, AlertCircle } from 'lucide-react';

const Waitlist: React.FC = () => {
    const [email, setEmail] = useState('');
    const [name, setName] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [submitted, setSubmitted] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);
        setError(null);

        try {
            if (!name.trim() || !email.trim()) {
                throw new Error('Name and email are required');
            }

            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                throw new Error('Please enter a valid email address');
            }

            const formData = new FormData();
            formData.append("form-name", "waitlist");
            formData.append("name", name);
            formData.append("email", email);

            await fetch("/", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: new URLSearchParams(formData as any).toString(),
            });

            setSubmitted(true);
            toast.success('You have been added to the waitlist!');

            setEmail('');
            setName('');
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
            setError(errorMessage);
            toast.error(errorMessage);
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <section id="waitlist" className="section bg-dark-lighter">
            <div className="container mx-auto px-6">
                <div className="max-w-4xl mx-auto bg-dark rounded-2xl p-8 md:p-12 border border-gray-800">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="text-center mb-8"
                    >
                        <h2 className="text-3xl md:text-4xl font-bold mb-4">
                            Join the <span className="gradient-text">Waitlist</span>
                        </h2>
                        <p className="text-gray-400">
                            Be among the first to experience Devr.AI and revolutionize your open-source community management.
                        </p>
                    </motion.div>

                    {submitted ? (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-green-900/30 border border-green-500 rounded-lg p-6 text-center"
                        >
                            <h3 className="text-xl font-semibold text-green-300 mb-2">Thanks for joining our waitlist!</h3>
                            <p className="text-gray-300">
                                We'll notify you when early access becomes available.
                                We're excited to have you on board!
                            </p>
                        </motion.div>
                    ) : (
                        <motion.form
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true }}
                            transition={{ delay: 0.2 }}
                            onSubmit={handleSubmit}
                            className="space-y-4"
                            name="waitlist"
                            method="POST"
                            data-netlify="true"
                            netlify-honeypot="bot-field"
                        >
                            {/* Netlify Forms hidden fields */}
                            <input type="hidden" name="form-name" value="waitlist" />
                            <p className="hidden">
                                <label>
                                    Don't fill this out if you're human: <input name="bot-field" />
                                </label>
                            </p>

                            {error && (
                                <div className="bg-red-900/30 border border-red-500 rounded-lg p-3 flex items-start gap-2 text-sm text-red-300">
                                    <AlertCircle className="shrink-0 mt-0.5" size={16} />
                                    <p>{error}</p>
                                </div>
                            )}

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label htmlFor="name" className="block text-sm font-medium text-gray-400 mb-1">
                                        Name
                                    </label>
                                    <input
                                        id="name"
                                        name="name"
                                        type="text"
                                        value={name}
                                        onChange={(e) => setName(e.target.value)}
                                        required
                                        placeholder="Your name"
                                        className="w-full px-4 py-3 bg-dark-card border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary text-white placeholder-gray-500"
                                    />
                                </div>
                                <div>
                                    <label htmlFor="email" className="block text-sm font-medium text-gray-400 mb-1">
                                        Email
                                    </label>
                                    <input
                                        id="email"
                                        name="email"
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                        placeholder="your@email.com"
                                        className="w-full px-4 py-3 bg-dark-card border border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary text-white placeholder-gray-500"
                                    />
                                </div>
                            </div>

                            <div className="flex flex-col items-center space-y-2">
                                <button
                                    type="submit"
                                    disabled={submitting}
                                    className="w-full md:w-auto btn-primary flex items-center justify-center gap-2 min-w-[200px]"
                                >
                                    {submitting ? (
                                        <motion.div
                                            animate={{ rotate: 360 }}
                                            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                            className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                                        />
                                    ) : (
                                        <>
                                            <Send size={18} />
                                            Join Waitlist
                                        </>
                                    )}
                                </button>
                                <p className="text-xs text-gray-500">
                                    We'll notify you when early access becomes available.
                                </p>
                            </div>
                        </motion.form>
                    )}
                </div>
            </div>
        </section>
    );
};

export default Waitlist;