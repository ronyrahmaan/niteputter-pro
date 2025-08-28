import React, { useState } from "react";
import { Link } from "react-router-dom";

const Home = () => {
  const [openFaq, setOpenFaq] = useState(null);

  const features = [
    {
      title: "Concept Design",
      description: "Revolutionary illuminated golf cup technology engineered for premium night putting experiences.",
      detail: "If traditional putting doesn't excite you, we revolutionize it. If it exists, we perfect it."
    },
    {
      title: "Manufacturing",
      description: "From prototype to production, our cups are engineered with patented POLY LIGHT CASING technology.",
      detail: "Built to spec. Delivered on time."
    },
    {
      title: "Integration Support",
      description: "Professional installation and ongoing support for golf courses and entertainment facilities.",
      detail: "We respond like we're part of your team—because we are."
    }
  ];

  const clients = [
    "GOLF COURSES",
    "ENTERTAINMENT CENTERS", 
    "RESIDENTIAL PROPERTIES",
    "HOSPITALITY VENUES",
    "RECREATION FACILITIES",
    "SPORTS COMPLEXES"
  ];

  const faqs = [
    {
      question: "How does the patented POLY LIGHT CASING protect the system?",
      answer: "Our patented technology protects the bulb from water and debris, ensuring easy maintenance and long-lasting performance in all weather conditions."
    },
    {
      question: "What makes the drainage system superior?",
      answer: "Engineered with multi-levels of drainage from top down, specifically designed to withstand heavy rains and flooding with mass flow technology."
    },
    {
      question: "Why choose hardwired over battery-powered systems?",
      answer: "Unlike competitors that require 8-hour charging for 4 hours of operation, our hardwired 12v low voltage system provides continuous operation without maintenance."
    },
    {
      question: "What's included in professional installation?",
      answer: "Complete system setup, wiring integration with existing landscape lighting, testing, and comprehensive training on operation and maintenance."
    }
  ];

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Loading Animation */}
      <section className="min-h-screen flex items-center justify-center relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-black via-gray-900 to-black"></div>
        
        <div className="relative z-10 max-w-4xl mx-auto px-6 text-center">
          <div className="mb-8 text-sm font-light tracking-widest text-gray-400">
            <div className="mb-2">[01] Initializing Night Golf Protocol...</div>
            <div className="mb-2 ml-8">// Verifying Lighting Systems</div>
            <div className="mb-2 ml-12">&gt;&gt; Establishing LED Connection</div>
            <div className="mb-2 ml-12">&gt;&gt; Checking Drainage Systems</div>
            <div className="mb-2 ml-8">// Authenticating Premium Quality</div>
            <div className="mb-2 ml-12">&gt;&gt; Confirming Veteran Engineering</div>
            <div className="mb-2 ml-12">&gt;&gt; Validating Texas Manufacturing</div>
            <div className="mb-4">Connection is secure -&gt;</div>
          </div>

          <h1 className="text-5xl md:text-8xl font-light mb-8 tracking-tight">
            PRECISION <span className="block">ENGINEERING</span>
          </h1>
          
          <p className="text-xl md:text-2xl font-light text-gray-300 mb-12 max-w-2xl mx-auto leading-relaxed">
            illuminated golf technology<br />
            and veteran-owned innovation
          </p>

          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <Link 
              to="/products"
              className="border border-white/30 text-white px-8 py-4 text-sm font-light tracking-wider hover:bg-white hover:text-black transition-all duration-300"
            >
              VIEW PRODUCTS
            </Link>
            <Link 
              to="/contact"
              className="text-sm font-light tracking-wider text-gray-400 px-8 py-4 hover:text-white transition-colors duration-300"
            >
              GET QUOTE
            </Link>
          </div>
        </div>
      </section>

      {/* Integrated Development Section */}
      <section className="py-32 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">
            <div>
              <h2 className="text-4xl md:text-6xl font-light mb-8 leading-tight">
                Integrated Night<br />
                <span className="text-gray-400">Golf Development</span>
              </h2>
              <div className="space-y-8 text-lg font-light text-gray-300">
                <div>
                  <strong className="text-white">Golf Courses</strong><br />
                  Professional installations
                </div>
                <div>
                  <strong className="text-white">Entertainment Centers</strong><br />
                  Premium experiences
                </div>
                <div>
                  <strong className="text-white">Residential Properties</strong><br />
                  Backyard putting and
                </div>
                <div>
                  <strong className="text-white">Immersive Lighting</strong><br />
                  experiences
                </div>
              </div>
            </div>

            <div className="space-y-12">
              {features.map((feature, index) => (
                <div key={index} className="border-l border-white/20 pl-8">
                  <h3 className="text-xl font-light text-white mb-4">{feature.title}</h3>
                  <p className="text-gray-400 font-light mb-4 leading-relaxed">{feature.description}</p>
                  <p className="text-sm text-gray-500 font-light italic">{feature.detail}</p>
                </div>
              ))}
              <Link 
                to="/technology"
                className="inline-block text-sm font-light tracking-wider text-white border-b border-white/30 hover:border-white transition-colors duration-300"
              >
                more
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Video Section */}
      <section className="py-32 px-6 bg-gray-900/30">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-4xl md:text-6xl font-light mb-8 leading-tight">
                See Our Technology<br />
                <span className="text-gray-400">In Action</span>
              </h2>
              <p className="text-lg font-light text-gray-300 mb-8 leading-relaxed">
                Watch our comprehensive demonstration of the Nite Putter Pro system. 
                From installation to operation, see why golf courses worldwide trust our veteran-engineered technology.
              </p>
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <span className="text-xs text-gray-500 mt-1">[01]</span>
                  <div>
                    <p className="text-white font-light">Patented POLY LIGHT CASING</p>
                    <p className="text-sm text-gray-400">Protected from water and debris</p>
                  </div>
                </div>
                <div className="flex items-start space-x-4">
                  <span className="text-xs text-gray-500 mt-1">[02]</span>
                  <div>
                    <p className="text-white font-light">Multi-Level Drainage</p>
                    <p className="text-sm text-gray-400">Withstands heavy rains and flooding</p>
                  </div>
                </div>
                <div className="flex items-start space-x-4">
                  <span className="text-xs text-gray-500 mt-1">[03]</span>
                  <div>
                    <p className="text-white font-light">Hardwired System</p>
                    <p className="text-sm text-gray-400">12v low voltage, no charging needed</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="relative">
              <div className="aspect-video bg-gray-800 rounded-sm overflow-hidden border border-white/10">
                <iframe
                  src="https://www.youtube.com/embed/gboU0jlwcrU"
                  title="Nite Putter Pro Technology"
                  className="w-full h-full"
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                ></iframe>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Veteran & Dedicated Section */}
      <section className="py-32 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div>
              <img 
                src="https://niteputterpro.com/wp-content/uploads/2024/07/PIC-1.jpg"
                alt="Nite Putter Pro Installation"
                className="w-full aspect-[4/3] object-cover grayscale hover:grayscale-0 transition-all duration-500"
                onError={(e) => {
                  e.target.src = "https://images.unsplash.com/photo-1699058455528-a603ab53c041?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzl8MHwxfHNlYXJjaHwzfHxuaWdodCUyMGdvbGZ8ZW58MHx8fHwxNzU1OTc0MTI1fDA&ixlib=rb-4.1.0&q=85";
                }}
              />
            </div>
            
            <div>
              <h2 className="text-4xl md:text-6xl font-light mb-12 leading-tight">
                Veteran-Owned<br />
                <span className="text-gray-400">& Dedicated</span>
              </h2>
              
              <div className="space-y-8">
                <div className="border-l border-white/20 pl-8">
                  <h3 className="text-xl font-light text-white mb-4">Quick to Start</h3>
                  <p className="text-gray-400 font-light leading-relaxed">
                    Delays burn time and budget. We are ready to move from planning to execution without stall.<br />
                    <span className="text-sm text-gray-500 italic">Downtime is engineered out of the equation.</span>
                  </p>
                </div>
                
                <div className="border-l border-white/20 pl-8">
                  <h3 className="text-xl font-light text-white mb-4">Clear, Fair Pricing</h3>
                  <p className="text-gray-400 font-light leading-relaxed">
                    High performance comes at a cost—but never a surprise. Premium quality with transparent pricing.<br />
                    <span className="text-sm text-gray-500 italic">No hidden variables.</span>
                  </p>
                </div>
                
                <div className="border-l border-white/20 pl-8">
                  <h3 className="text-xl font-light text-white mb-4">Professional Integration</h3>
                  <p className="text-gray-400 font-light leading-relaxed">
                    Our specialists use industry proven workflows for seamless installation.<br />
                    <span className="text-sm text-gray-500 italic">Zero cleanup.</span>
                  </p>
                </div>
              </div>
              
              <a 
                href="tel:469-642-7171"
                className="inline-block mt-12 text-sm font-light tracking-wider text-white border-b border-white/30 hover:border-white transition-colors duration-300"
              >
                contact us
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Clients Section */}
      <section className="py-32 px-6 bg-gray-900/30">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-4xl md:text-6xl font-light mb-16 leading-tight text-center">
            select installations<br />
            <span className="text-gray-400">we've completed</span>
          </h2>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8 text-center">
            {clients.map((client, index) => (
              <div key={index} className="text-sm font-light tracking-wider text-gray-400 hover:text-white transition-colors duration-300 cursor-default">
                {client}
              </div>
            ))}
          </div>
          
          <div className="mt-16 text-center">
            <img 
              src="https://niteputterpro.com/wp-content/uploads/2024/07/pic-3-1.jpg"
              alt="Professional Installation"
              className="w-full max-w-2xl mx-auto aspect-video object-cover grayscale hover:grayscale-0 transition-all duration-500"
              onError={(e) => {
                e.target.src = "https://images.unsplash.com/photo-1660165458059-57cfb6cc87e5?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDk1Nzd8MHwxfHNlYXJjaHwzfHxmdXR1cmlzdGljJTIwdGVjaG5vbG9neXxlbnwwfHx8fDE3NTU5NzQxMzF8MA&ixlib=rb-4.1.0&q=85";
              }}
            />
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-32 px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-4xl md:text-6xl font-light mb-16 leading-tight">
            frequently asked<br />
            <span className="text-gray-400">questions</span>
          </h2>
          
          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <div key={index} className="border-b border-white/10">
                <button
                  className="w-full py-6 text-left flex justify-between items-start hover:text-gray-300 transition-colors duration-300"
                  onClick={() => setOpenFaq(openFaq === index ? null : index)}
                >
                  <div className="flex-1">
                    <span className="text-xs text-gray-500 mr-4">[0{index + 1}]</span>
                    <span className="text-lg font-light">{faq.question}</span>
                  </div>
                  <div className="ml-4 text-2xl font-light text-gray-400">
                    {openFaq === index ? '−' : '+'}
                  </div>
                </button>
                {openFaq === index && (
                  <div className="pb-6 ml-8">
                    <p className="text-gray-400 font-light leading-relaxed">{faq.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 px-6 bg-gray-900/30">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-6xl font-light mb-8 leading-tight">
            Ready to transform<br />
            <span className="text-gray-400">your golf experience?</span>
          </h2>
          <p className="text-lg font-light text-gray-300 mb-12 leading-relaxed max-w-2xl mx-auto">
            Professional installation and ongoing support from our veteran-owned team. 
            Based in Heath, Texas, serving installations nationwide.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <a
              href="tel:469-642-7171"
              className="border border-white/30 text-white px-8 py-4 text-sm font-light tracking-wider hover:bg-white hover:text-black transition-all duration-300"
            >
              CALL: (469) 642-7171
            </a>
            <Link
              to="/contact"
              className="text-sm font-light tracking-wider text-gray-400 px-8 py-4 hover:text-white transition-colors duration-300"
            >
              GET DETAILED QUOTE
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;