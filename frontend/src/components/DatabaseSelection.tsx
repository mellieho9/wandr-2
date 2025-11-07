import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Checkbox } from './ui/checkbox';
import { Label } from './ui/label';
import { motion, AnimatePresence } from 'motion/react';

interface NotionDatabase {
  id: string;
  name: string;
  icon?: string;
}

interface SelectedDatabase extends NotionDatabase {
  tag: string;
}

// Mock Notion databases
const mockDatabases: NotionDatabase[] = [
  { id: '1', name: 'Places to Visit', icon: '📍' },
  { id: '2', name: 'Restaurants', icon: '🍽️' },
  { id: '3', name: 'Coffee Shops', icon: '☕' },
  { id: '4', name: 'Shopping', icon: '🛍️' },
  { id: '5', name: 'Travel Ideas', icon: '✈️' },
];

export function DatabaseSelection() {
  const [selectedDatabases, setSelectedDatabases] = useState<Map<string, string>>(new Map());
  const [isConfigured, setIsConfigured] = useState(false);

  const handleToggleDatabase = (database: NotionDatabase, checked: boolean) => {
    const newSelected = new Map(selectedDatabases);
    if (checked) {
      // Generate a default tag from the database name
      const defaultTag = database.name.toLowerCase().replace(/\s+/g, '-');
      newSelected.set(database.id, defaultTag);
    } else {
      newSelected.delete(database.id);
    }
    setSelectedDatabases(newSelected);
  };

  const handleTagChange = (databaseId: string, tag: string) => {
    const newSelected = new Map(selectedDatabases);
    newSelected.set(databaseId, tag);
    setSelectedDatabases(newSelected);
  };

  const handleSaveConfiguration = () => {
    console.log('Saving configuration:', Array.from(selectedDatabases.entries()));
    setIsConfigured(true);
  };

  if (isConfigured) {
    return (
      <div className="min-h-screen flex items-center justify-center px-6 bg-[#F7F6F3]">
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4, ease: "easeOut" }}
          className="max-w-md mx-auto text-center space-y-6"
        >
          <div className="space-y-3">
            <motion.div 
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200, damping: 15 }}
              className="text-4xl"
            >
              ✓
            </motion.div>
            <div className="space-y-1">
              <p className="text-black">You're all set</p>
              <p className="text-sm text-gray-600">
                Start pasting TikTok links into your databases
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen px-6 py-20 bg-[#F7F6F3]">
      <div className="max-w-2xl mx-auto space-y-8">
        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="space-y-2"
        >
          <h1 className="text-3xl text-black">Connect your databases</h1>
          <p className="text-gray-600">
            Pick where you want to save TikToks. You can add tags to organize things later.
          </p>
        </motion.div>

        {/* Database List */}
        <div className="space-y-0 border-t border-gray-300">
          {mockDatabases.map((database, index) => {
            const isSelected = selectedDatabases.has(database.id);
            const currentTag = selectedDatabases.get(database.id) || '';

            return (
              <motion.div 
                key={database.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1, duration: 0.3 }}
                className="border-b border-gray-300 py-5"
              >
                <div className="flex items-start gap-3">
                  <Checkbox
                    id={database.id}
                    checked={isSelected}
                    onCheckedChange={(checked) => handleToggleDatabase(database, checked as boolean)}
                    className="mt-0.5"
                  />
                  <div className="flex-1 space-y-3">
                    <Label htmlFor={database.id} className="flex items-center gap-2 cursor-pointer text-black">
                      <span>{database.icon}</span>
                      <span>{database.name}</span>
                    </Label>

                    <AnimatePresence>
                      {isSelected && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.2 }}
                          className="flex items-center gap-2 pl-6"
                        >
                          <span className="text-gray-400 text-sm">#</span>
                          <Input
                            id={`tag-${database.id}`}
                            value={currentTag}
                            onChange={(e) => handleTagChange(database.id, e.target.value)}
                            placeholder="tag"
                            className="text-sm border-0 border-b border-gray-300 rounded-none px-0 focus-visible:ring-0 focus-visible:border-black bg-transparent"
                          />
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Action Buttons */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.3 }}
          className="flex items-center justify-between pt-4"
        >
          <p className="text-sm text-gray-600">
            {selectedDatabases.size === 0 ? 'Select at least one' : `${selectedDatabases.size} selected`}
          </p>
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            transition={{ type: "spring", stiffness: 400, damping: 17 }}
          >
            <Button
              onClick={handleSaveConfiguration}
              disabled={selectedDatabases.size === 0}
              className="bg-black hover:bg-gray-900 text-white disabled:bg-gray-300 disabled:text-gray-500"
            >
              Continue
            </Button>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}