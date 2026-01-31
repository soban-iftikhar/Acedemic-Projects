#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <pthread.h>
#include <algorithm> // for std::count

using namespace std;

// --- Shared Data and Synchronization ---

// Global structure to hold shared results
struct AnalysisResults {
    long total_chars;
    long total_lines;
    long total_words;
    long term_occurrences;
};

// Global instance of the results, shared among all threads
AnalysisResults shared_results = {0, 0, 0, 0};
// Mutex lock to protect access to the shared_results structure
pthread_mutex_t mutex_lock;

// The search term specified for this run
const string SEARCH_TERM = "threads"; // The term to count occurrences of

// --- Data Structure for Thread Input ---

// Structure passed to each thread containing its specific analysis section
struct ThreadData {
    string content_section;
};


// --- Thread Function ---

// This function is executed by each thread
void* analyze_section(void* arg) {
    ThreadData* data = (ThreadData*)arg;
    stringstream ss(data->content_section);
    string line;

    // Local counters for this specific thread
    long local_chars = 0;
    long local_lines = 0;
    long local_words = 0;
    long local_term_occurrences = 0;
    
    // Process the content line by line
    while (getline(ss, line)) {
        local_lines++;
        local_chars += line.length() + 1; // +1 for the newline character
        
        string word;
        stringstream line_stream(line);
        
        // Process the line word by word
        while (line_stream >> word) {
            local_words++;
            // Simple check for the search term (case sensitive)
            if (word.find(SEARCH_TERM) != string::npos) {
                local_term_occurrences++;
            }
        }
    }

    // --- Critical Section: Combining Results using Mutex ---
    
    // Acquire the lock before accessing shared_results
    pthread_mutex_lock(&mutex_lock);

    // Update the shared global counters (Critical Section)
    shared_results.total_chars += local_chars;
    shared_results.total_lines += local_lines;
    shared_results.total_words += local_words;
    shared_results.term_occurrences += local_term_occurrences;

    // Release the lock
    pthread_mutex_unlock(&mutex_lock);

    pthread_exit(NULL);
}


// --- Main Program ---

int main(int argc, char* argv[]) {
    cout << "--- Linux System Guardian: Multithreaded File Analyzer ---" << endl;
    
    // Check for correct command line usage (input file)
    if (argc < 2) {
        cerr << "Usage: " << argv[0] << " <input_file>" << endl;
        return 1;
    }
    
    const char* filename = argv[1];
    
    // Read the entire file content into a single string
    ifstream file(filename);
    if (!file.is_open()) {
        cerr << "Error: Could not open file " << filename << endl;
        return 1;
    }
    
    // Get file size and read content
    file.seekg(0, ios::end);
    long file_size = file.tellg();
    string file_content(file_size, ' ');
    file.seekg(0, ios::beg);
    file.read(&file_content[0], file_size);
    file.close();

    // Determine the number of threads (e.g., 4 threads)
    int num_threads = 4;
    pthread_t threads[num_threads];
    vector<ThreadData> thread_data(num_threads);
    
    // Initialize the Mutex
    if (pthread_mutex_init(&mutex_lock, NULL) != 0) {
        cerr << "Mutex initialization failed" << endl;
        return 1;
    }

    // --- Divide Content and Create Threads ---

    int section_size = file_content.length() / num_threads;
    cout << "Analyzing file: " << filename << " using " << num_threads << " threads." << endl;
    cout << "Search term: '" << SEARCH_TERM << "'" << endl;

    for (int i = 0; i < num_threads; ++i) {
        int start = i * section_size;
        int end = (i == num_threads - 1) ? file_content.length() : (i + 1) * section_size;
        
        // Ensure the split doesn't happen mid-word by finding the next newline
        if (i < num_threads - 1 && end < file_content.length()) {
            end = file_content.find('\n', end);
            if (end == string::npos) {
                end = file_content.length();
            } else {
                end++; // Include the newline in the section
            }
        }
        
        thread_data[i].content_section = file_content.substr(start, end - start);
        
        // Create the thread and execute the analysis function
        if (pthread_create(&threads[i], NULL, analyze_section, &thread_data[i]) != 0) {
            cerr << "Error creating thread " << i << endl;
            return 1;
        }
        cout << "Created thread " << i+1 << " to analyze section from " << start << " to " << end << endl;
    }
    
    // --- Synchronization: Wait for all threads to finish ---
    
    // Wait for every thread to complete its execution (join)
    for (int i = 0; i < num_threads; ++i) {
        pthread_join(threads[i], NULL);
    }
    
    // Destroy the Mutex
    pthread_mutex_destroy(&mutex_lock);

    // --- Display Final Results ---
    
    cout << "\n--- Final Analysis Results ---" << endl;
    cout << "Total Characters: " << shared_results.total_chars << endl;
    cout << "Total Lines:      " << shared_results.total_lines << endl;
    cout << "Total Words:      " << shared_results.total_words << endl;
    cout << "Term ('" << SEARCH_TERM << "') Occurrences: " << shared_results.term_occurrences << endl;
    cout << "Module 3 demonstration complete." << endl;

    return 0;
}