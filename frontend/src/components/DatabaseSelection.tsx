import { useState, useEffect } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Checkbox } from "./ui/checkbox";
import { Label } from "./ui/label";
import { motion, AnimatePresence } from "motion/react";
import { API_ENDPOINTS } from "../config";

interface NotionDatabase {
  id: string;
  title: string;
  icon?: {
    type: string;
    emoji?: string;
  };
}

export function DatabaseSelection() {
  const [databases, setDatabases] = useState<NotionDatabase[]>([]);
  const [selectedDatabases, setSelectedDatabases] = useState<
    Map<string, string>
  >(new Map());
  const [isConfigured, setIsConfigured] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  // Fetch available databases on mount
  useEffect(() => {
    fetchAvailableDatabases();
  }, []);

  const fetchAvailableDatabases = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch(API_ENDPOINTS.DATABASES_AVAILABLE, {
        credentials: "include", // Include session cookie
      });

      if (!response.ok) {
        const errorData = await response
          .json()
          .catch(() => ({ error: "Failed to fetch databases" }));
        throw new Error(errorData.error || "Failed to fetch databases");
      }

      const data = await response.json();
      setDatabases(data.databases || []);
    } catch (err) {
      console.error("Error fetching databases:", err);
      setError(err instanceof Error ? err.message : "Failed to load databases");
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleDatabase = (database: NotionDatabase, checked: boolean) => {
    const newSelected = new Map(selectedDatabases);
    if (checked) {
      // Generate a default tag from the database title
      const defaultTag = database.title.toLowerCase().replace(/\s+/g, "-");
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

  const handleSaveConfiguration = async () => {
    try {
      setIsSaving(true);
      setError(null);

      // Register each selected database
      const registrationPromises = Array.from(selectedDatabases.entries()).map(
        async ([dbId, tag]) => {
          const response = await fetch(API_ENDPOINTS.DATABASES_REGISTER, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            credentials: "include",
            body: JSON.stringify({
              db_id: dbId,
              tag: tag,
            }),
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || "Failed to register database");
          }

          return response.json();
        }
      );

      await Promise.all(registrationPromises);
      setIsConfigured(true);
    } catch (err) {
      console.error("Error saving configuration:", err);
      setError(
        err instanceof Error ? err.message : "Failed to save configuration"
      );
    } finally {
      setIsSaving(false);
    }
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
              transition={{
                delay: 0.2,
                type: "spring",
                stiffness: 200,
                damping: 15,
              }}
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

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center px-6 bg-[#F7F6F3]">
        <div className="text-center space-y-4">
          <div className="text-gray-600">Loading your databases...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center px-6 bg-[#F7F6F3]">
        <div className="max-w-md mx-auto text-center space-y-4">
          <div className="text-red-600">Error: {error}</div>
          <Button
            onClick={fetchAvailableDatabases}
            className="bg-black hover:bg-gray-900 text-white"
          >
            Retry
          </Button>
        </div>
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
            Pick where you want to save TikToks. You can add tags to organize
            things later.
          </p>
        </motion.div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Database List */}
        <div className="space-y-0 border-t border-gray-300">
          {databases.length === 0 ? (
            <div className="py-8 text-center text-gray-600">
              No databases found. Create a database in Notion first.
            </div>
          ) : (
            databases.map((database, index) => {
              const isSelected = selectedDatabases.has(database.id);
              const currentTag = selectedDatabases.get(database.id) || "";
              const emoji = database.icon?.emoji || "📄";

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
                      onCheckedChange={(checked) =>
                        handleToggleDatabase(database, checked as boolean)
                      }
                      className="mt-0.5"
                    />
                    <div className="flex-1 space-y-3">
                      <Label
                        htmlFor={database.id}
                        className="flex items-center gap-2 cursor-pointer text-black"
                      >
                        <span>{emoji}</span>
                        <span>{database.title}</span>
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
                              onChange={(e) =>
                                handleTagChange(database.id, e.target.value)
                              }
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
            })
          )}
        </div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.3 }}
          className="flex items-center justify-between pt-4"
        >
          <p className="text-sm text-gray-600">
            {selectedDatabases.size === 0
              ? "Select at least one"
              : `${selectedDatabases.size} selected`}
          </p>
          <motion.div
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            transition={{ type: "spring", stiffness: 400, damping: 17 }}
          >
            <Button
              onClick={handleSaveConfiguration}
              disabled={selectedDatabases.size === 0 || isSaving}
              className="bg-black hover:bg-gray-900 text-white disabled:bg-gray-300 disabled:text-gray-500"
            >
              {isSaving ? "Saving..." : "Continue"}
            </Button>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
