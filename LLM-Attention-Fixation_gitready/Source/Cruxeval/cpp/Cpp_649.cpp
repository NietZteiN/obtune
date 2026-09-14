#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long tabsize) {
    std::stringstream ss(text);
    std::string line, result;
    
    while(std::getline(ss, line, '\n')) {
        for(char& c : line) {
            if(c == '\t') {
                result += std::string(tabsize, ' ');
            } else {
                result += c;
            }
        }
        result += '\n';
    }
    result.pop_back();  // remove the last newline character
    
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("	f9\n	ldf9\n	adf9!\n	f9?"), (1)) == (" f9\n ldf9\n adf9!\n f9?"));
}
