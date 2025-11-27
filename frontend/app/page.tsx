'use client';

// Demo Copilot - Autonomous AI Sales Engineer
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Sparkles, Play, Clock, CheckCircle } from 'lucide-react';

export default function HomePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    demo_type: 'insign',
    customer_name: '',
    customer_email: '',
    customer_company: '',
    demo_duration: 'standard'
  });

  const handleStartDemo = async () => {
    setLoading(true);

    try {
      // Get backend URL from environment variable
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/api/demo/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      // Check if the response was successful
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to start demo');
      }

      // Validate session_id exists
      if (!data.session_id) {
        throw new Error('Invalid response: missing session_id');
      }

      // Navigate to demo page
      router.push(`/demo/${data.session_id}`);

    } catch (error) {
      console.error('Error starting demo:', error);
      alert(`Failed to start demo: ${error instanceof Error ? error.message : 'Please try again.'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <Sparkles className="w-12 h-12 text-indigo-600 mr-2" />
            <h1 className="text-5xl font-bold text-gray-900">Demo Copilot</h1>
          </div>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Experience our products with an AI-powered sales engineer.
            Get a personalized, interactive demo in minutes.
          </p>
        </div>

        {/* Demo Selection Cards */}
        <div className="grid md:grid-cols-2 gap-6 mb-12 max-w-4xl mx-auto">
          <Card className={`cursor-pointer transition-all ${formData.demo_type === 'insign' ? 'ring-2 ring-indigo-600' : ''}`}
                onClick={() => setFormData({...formData, demo_type: 'insign'})}>
            <CardHeader>
              <CardTitle>InSign</CardTitle>
              <CardDescription>Electronic signature platform</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
                  50-70% cheaper than DocuSign
                </li>
                <li className="flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
                  Unlimited users
                </li>
                <li className="flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
                  Free audit trails
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card className={`cursor-pointer transition-all ${formData.demo_type === 'crew_intelligence' ? 'ring-2 ring-indigo-600' : ''}`}
                onClick={() => setFormData({...formData, demo_type: 'crew_intelligence'})}>
            <CardHeader>
              <CardTitle>Crew Intelligence</CardTitle>
              <CardDescription>AI-powered crew operations for airlines</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
                  30% reduction in pay claims
                </li>
                <li className="flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
                  Voice AI assistant
                </li>
                <li className="flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2 text-green-500" />
                  FAA compliance monitoring
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>

        {/* Form */}
        <Card className="max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle>Get Your AI-Powered Demo</CardTitle>
            <CardDescription>
              Start your demo instantly. Details are optional for personalization.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">Your Name <span className="text-gray-400">(optional)</span></Label>
                <Input
                  id="name"
                  placeholder="Jayaprakash"
                  value={formData.customer_name}
                  onChange={(e) => setFormData({...formData, customer_name: e.target.value})}
                />
              </div>
              <div>
                <Label htmlFor="email">Email <span className="text-gray-400">(optional)</span></Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@company.com"
                  value={formData.customer_email}
                  onChange={(e) => setFormData({...formData, customer_email: e.target.value})}
                />
              </div>
            </div>

            <div>
              <Label htmlFor="company">Company <span className="text-gray-400">(optional)</span></Label>
              <Input
                id="company"
                placeholder="Number Labs"
                value={formData.customer_company}
                onChange={(e) => setFormData({...formData, customer_company: e.target.value})}
              />
            </div>

            <div>
              <Label htmlFor="duration">Demo Duration</Label>
              <Select value={formData.demo_duration}
                      onValueChange={(value) => setFormData({...formData, demo_duration: value})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="quick">
                    <div className="flex items-center">
                      <Clock className="w-4 h-4 mr-2" />
                      Quick (5 minutes)
                    </div>
                  </SelectItem>
                  <SelectItem value="standard">
                    <div className="flex items-center">
                      <Clock className="w-4 h-4 mr-2" />
                      Standard (10 minutes)
                    </div>
                  </SelectItem>
                  <SelectItem value="deep_dive">
                    <div className="flex items-center">
                      <Clock className="w-4 h-4 mr-2" />
                      Deep Dive (20 minutes)
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button
              className="w-full"
              size="lg"
              onClick={handleStartDemo}
              disabled={loading}
            >
              {loading ? (
                <>Loading...</>
              ) : (
                <>
                  <Play className="w-5 h-5 mr-2" />
                  Start AI Demo
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Features */}
        <div className="mt-16 max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-8">Why Demo Copilot?</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-indigo-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Sparkles className="w-8 h-8 text-indigo-600" />
              </div>
              <h3 className="font-semibold mb-2">AI-Powered</h3>
              <p className="text-sm text-gray-600">
                Natural conversations with Claude AI
              </p>
            </div>
            <div className="text-center">
              <div className="bg-indigo-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Clock className="w-8 h-8 text-indigo-600" />
              </div>
              <h3 className="font-semibold mb-2">24/7 Available</h3>
              <p className="text-sm text-gray-600">
                Get demos anytime, anywhere
              </p>
            </div>
            <div className="text-center">
              <div className="bg-indigo-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-indigo-600" />
              </div>
              <h3 className="font-semibold mb-2">Interactive</h3>
              <p className="text-sm text-gray-600">
                Ask questions and dive deeper
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
