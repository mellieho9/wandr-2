import { Button } from "./ui/button";
import { motion } from "motion/react";
import { Link, Sparkles, MapPin } from "lucide-react";
import { CIcon } from "@coreui/icons-react";
import { cibNotion } from "@coreui/icons";
import { API_ENDPOINTS } from "../config";

interface LandingPageProps {
  onAuthenticate: () => void;
}

export function LandingPage({ onAuthenticate }: LandingPageProps) {
  const handleNotionConnect = () => {
    // Redirect to Flask OAuth endpoint
    window.location.href = API_ENDPOINTS.AUTH_LOGIN;
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F7F6F3]">
      {/* Hero Section */}
      <main className="flex-1 px-6 py-20">
        <div className="max-w-2xl mx-auto space-y-12">
          {/* Main Heading */}
          <div className="space-y-4">
            <h1 className="text-4xl text-black">
              Stop screenshotting TikToks you'll never look at again
            </h1>
            <p className="text-gray-600">
              See a cool restaurant on TikTok? Wandr automatically saves it to
              your Notion with the address, hours, and a Google Maps link. No
              more forgotten screenshots.
            </p>
          </div>

          {/* How It Works */}
          <div className="space-y-6">
            <div className="flex gap-4">
              <div className="w-10 h-10 rounded-lg bg-white border border-gray-300 flex items-center justify-center shrink-0">
                <Link className="w-5 h-5 text-black" />
              </div>
              <div className="space-y-1 pt-1">
                <div className="text-black">Paste any TikTok link</div>
                <div className="text-sm text-gray-600">
                  Found a cool spot? Just drop the URL into your Notion database
                </div>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-10 h-10 rounded-lg bg-white border border-gray-300 flex items-center justify-center shrink-0">
                <Sparkles className="w-5 h-5 text-black" />
              </div>
              <div className="space-y-1 pt-1">
                <div className="text-black">We handle the rest</div>
                <div className="text-sm text-gray-600">
                  AI extracts business names, addresses, and verifies everything
                  with Google Maps
                </div>
              </div>
            </div>

            <div className="flex gap-4">
              <div className="w-10 h-10 rounded-lg bg-white border border-gray-300 flex items-center justify-center shrink-0">
                <MapPin className="w-5 h-5 text-black" />
              </div>
              <div className="space-y-1 pt-1">
                <div className="text-black">Actually use your discoveries</div>
                <div className="text-sm text-gray-600">
                  Search through everything or ask AI to help you plan your next
                  outing
                </div>
              </div>
            </div>
          </div>

          {/* CTA */}
          <div className="pt-4">
            <motion.div
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.99 }}
              transition={{ type: "spring", stiffness: 400, damping: 17 }}
            >
              <Button
                size="lg"
                onClick={handleNotionConnect}
                className="bg-black hover:bg-gray-900 text-white px-5 py-5 w-full sm:w-auto transition-colors duration-150"
              >
                <CIcon icon={cibNotion} className="text-white" />
                Continue with Notion
              </Button>
            </motion.div>
            <p className="text-xs text-gray-500 mt-3">
              Free to start • Takes 2 minutes to setup
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
