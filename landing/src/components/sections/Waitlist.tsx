import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { Send, AlertCircle, CheckCircle, Sparkles } from 'lucide-react';

const Waitlist: React.FC = () => {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [organization, setOrganization] = useState('');
  const [role, setRole] = useState('');
  const [suggestions, setSuggestions] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  const roleOptions = [
    "Student (Currently in school, university, or bootcamp)",
    "Working Professional (Employed in tech or a related field)",
    "Business Professional (Entrepreneur, startup founder, or executive)",
    "Open Source & Community Member (Contributor, maintainer, or community volunteer)",
    "Other:"
  ];

  const FORM_ID = '1FAIpQLSet1YnQTfOmfSzDblYxTXHSEHDhT4l7_LoqtN-5k-WUJAZUBw';
  const FORM_URL = `https://docs.google.com/forms/d/e/${FORM_ID}/formResponse`;

  const FIELD_MAPPINGS = {
    name: 'entry.1958162697',
    email: 'entry.1305603809',
    organization: 'entry.1486768385',
    role: 'entry.1449836771',
    suggestions: 'entry.1484217632'
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      if (!name.trim() || !email.trim() || !organization.trim() || !role) {
        throw new Error('All fields are required except suggestions');
      }

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        throw new Error('Please enter a valid email address');
      }

      const formData = new URLSearchParams();
      formData.append(FIELD_MAPPINGS.name, name);
      formData.append(FIELD_MAPPINGS.email, email);
      formData.append(FIELD_MAPPINGS.organization, organization);
      formData.append(FIELD_MAPPINGS.role, role);
      if (suggestions) {
        formData.append(FIELD_MAPPINGS.suggestions, suggestions);
      }

      await fetch(FORM_URL, {
        method: 'POST',
        mode: 'no-cors',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData.toString()
      });

      setSubmitted(true);
      toast.success('You have been added to the waitlist!');
      
      setEmail('');
      setName('');
      setOrganization('');
      setRole('');
      setSuggestions('');
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section id="waitlist" className="section relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-secondary/5 blur-3xl" />
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-primary/10 to-secondary/10 rounded-full blur-3xl" />
      
      <div className="container mx-auto px-6 relative z-10">
        <div className="max-w-4xl mx-auto">
          {/* Gradient border container */}
          <div className="relative p-[1px] bg-gradient-to-r from-primary via-secondary to-primary rounded-2xl">
            <div className="bg-dark/95 backdrop-blur-xl rounded-2xl p-8 md:p-12">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                className="text-center mb-8"
              >
                <div className="flex items-center justify-center gap-2 mb-4">
                  <Sparkles className="text-primary" size={24} />
                  <h2 className="text-3xl md:text-4xl font-bold">
                    Join the <span className="gradient-text">Waitlist</span>
                  </h2>
                  <Sparkles className="text-secondary" size={24} />
                </div>
                <p className="text-gray-400 text-lg">
                  Be among the first to experience Devr.AI and revolutionize your open-source community management.
                </p>
              </motion.div>

              {submitted ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="relative"
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-green-500/20 to-emerald-500/20 rounded-xl blur-xl" />
                  <div className="relative bg-gradient-to-r from-green-900/40 to-emerald-900/40 border border-green-500/50 rounded-xl p-8 text-center backdrop-blur-sm">
                    <div className="flex items-center justify-center mb-4">
                      <CheckCircle className="text-green-400" size={48} />
                    </div>
                    <h3 className="text-2xl font-bold text-green-300 mb-3">Welcome to the future!</h3>
                    <p className="text-gray-300 text-lg">
                      You're now on our exclusive waitlist. We'll notify you the moment early access becomes available.
                    </p>
                    <div className="mt-6 p-4 bg-green-900/20 rounded-lg border border-green-500/30">
                      <p className="text-green-400 font-medium">
                        🎉 Keep an eye on your inbox for exciting updates!
                      </p>
                    </div>
                  </div>
                </motion.div>
              ) : (
                <motion.form
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.2 }}
                  onSubmit={handleSubmit}
                  className="space-y-6"
                >
                  {error && (
                    <motion.div
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="relative"
                    >
                      <div className="absolute inset-0 bg-gradient-to-r from-red-500/20 to-orange-500/20 rounded-lg blur-sm" />
                      <div className="relative bg-red-900/40 border border-red-500/50 rounded-lg p-4 flex items-start gap-3 backdrop-blur-sm">
                        <AlertCircle className="shrink-0 mt-0.5 text-red-400" size={20} />
                        <p className="text-red-300 font-medium">{error}</p>
                      </div>
                    </motion.div>
                  )}

                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label htmlFor="name" className="block text-sm font-semibold text-gray-300 mb-2">
                        Full Name
                      </label>
                      <div className="relative group">
                        <div className="absolute inset-0 bg-gradient-to-r from-primary/50 to-secondary/50 rounded-xl blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                        <input
                          id="name"
                          name="name"
                          type="text"
                          value={name}
                          onChange={(e) => setName(e.target.value)}
                          required
                          placeholder="Enter your full name"
                          className="relative w-full px-4 py-4 bg-dark-card/80 border border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 text-white placeholder-gray-500 backdrop-blur-sm transition-all duration-300 hover:border-gray-600"
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <label htmlFor="email" className="block text-sm font-semibold text-gray-300 mb-2">
                        Email Address
                      </label>
                      <div className="relative group">
                        <div className="absolute inset-0 bg-gradient-to-r from-primary/50 to-secondary/50 rounded-xl blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                        <input
                          id="email"
                          name="email"
                          type="email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          required
                          placeholder="your@email.com"
                          className="relative w-full px-4 py-4 bg-dark-card/80 border border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 text-white placeholder-gray-500 backdrop-blur-sm transition-all duration-300 hover:border-gray-600"
                        />
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="organization" className="block text-sm font-semibold text-gray-300 mb-2">
                      Organization
                    </label>
                    <div className="relative group">
                      <div className="absolute inset-0 bg-gradient-to-r from-primary/50 to-secondary/50 rounded-xl blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                      <input
                        id="organization"
                        name="organization"
                        type="text"
                        value={organization}
                        onChange={(e) => setOrganization(e.target.value)}
                        required
                        placeholder="Your company, university, or organization"
                        className="relative w-full px-4 py-4 bg-dark-card/80 border border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 text-white placeholder-gray-500 backdrop-blur-sm transition-all duration-300 hover:border-gray-600"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="role" className="block text-sm font-semibold text-gray-300 mb-2">
                      Your Role
                    </label>
                    <div className="relative group">
                      <div className="absolute inset-0 bg-gradient-to-r from-primary/50 to-secondary/50 rounded-xl blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                      <select
                        id="role"
                        name="role"
                        value={role}
                        onChange={(e) => setRole(e.target.value)}
                        required
                        className="relative w-full px-4 py-4 bg-dark-card/80 border border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 text-white backdrop-blur-sm transition-all duration-300 hover:border-gray-600"
                      >
                        <option value="" className="bg-dark-card">Select your role</option>
                        {roleOptions.map((option) => (
                          <option key={option} value={option} className="bg-dark-card">
                            {option}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="suggestions" className="block text-sm font-semibold text-gray-300 mb-2">
                      Suggestions & Comments <span className="text-gray-500 font-normal">(optional)</span>
                    </label>
                    <div className="relative group">
                      <div className="absolute inset-0 bg-gradient-to-r from-primary/50 to-secondary/50 rounded-xl blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                      <textarea
                        id="suggestions"
                        name="suggestions"
                        value={suggestions}
                        onChange={(e) => setSuggestions(e.target.value)}
                        placeholder="Share your thoughts, feature requests, or any feedback..."
                        className="relative w-full px-4 py-4 bg-dark-card/80 border border-gray-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 text-white placeholder-gray-500 backdrop-blur-sm transition-all duration-300 hover:border-gray-600 resize-none"
                        rows={4}
                      />
                    </div>
                  </div>

                  <div className="flex flex-col items-center space-y-4 pt-4">
                    <div className="relative group">
                      <div className="absolute inset-0 bg-gradient-to-r from-primary to-secondary rounded-xl blur-lg opacity-75 group-hover:opacity-100 transition-opacity duration-300" />
                      <button
                        type="submit"
                        disabled={submitting}
                        className="relative w-full md:w-auto bg-gradient-to-r from-black via-green-500 to-black hover:from-black hover:via-green-400 hover:to-black text-white font-bold py-4 px-8 rounded-xl flex items-center justify-center gap-3 min-w-[250px] transition-all duration-500 ease-in-out transform hover:scale-105 hover:shadow-2xl hover:shadow-green-500/25 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-lg active:scale-95"
                      >
                        {submitting ? (
                          <>
                            <motion.div
                              animate={{ rotate: 360 }}
                              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                              className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                            />
                            <span>Joining Waitlist...</span>
                          </>
                        ) : (
                          <>
                            <Send size={20} />
                            <span>Join Waitlist</span>
                          </>
                        )}
                      </button>
                    </div>
                    
                    <div className="text-center space-y-2">
                      <p className="text-sm text-gray-400">
                        🚀 We'll notify you when early access becomes available
                      </p>
                      <p className="text-xs text-gray-500">
                        Join <span className="text-primary font-semibold">1000+</span> developers already on the list
                      </p>
                    </div>
                  </div>
                </motion.form>
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Waitlist;