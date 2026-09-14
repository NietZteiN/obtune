#include<assert.h>
#include<bits/stdc++.h>
long f(std::string txt) {
    std::unordered_map<char, int> coincidences;
    for (char c : txt) {
        if (coincidences.find(c) != coincidences.end()) {
            coincidences[c]++;
        } else {
            coincidences[c] = 1;
        }
    }
    
    int sum = 0;
    for (auto& pair : coincidences) {
        sum += pair.second;
    }
    
    return sum;
}
int main() {
    auto candidate = f;
    assert(candidate(("11 1 1")) == (6));
}
