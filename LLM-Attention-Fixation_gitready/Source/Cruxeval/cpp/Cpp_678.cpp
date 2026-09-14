#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,long> f(std::string text) {
    std::map<std::string, long> freq;
    for(char c : text) {
        if(isalpha(c)) {
            std::string key(1, std::tolower(c));
            if(freq.find(key) != freq.end()) {
                freq[key]++;
            } else {
                freq[key] = 1;
            }
        }
    }
    return freq;
}
int main() {
    auto candidate = f;
    assert(candidate(("HI")) == (std::map<std::string,long>({{"h", 1}, {"i", 1}})));
}
