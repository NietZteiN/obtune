#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::string text) {
    std::unordered_map<char, int> occ;
    for (char ch : text) {
        std::unordered_map<char, char> name = {{'a', 'b'}, {'b', 'c'}, {'c', 'd'}, {'d', 'e'}, {'e', 'f'}};
        char newName = name.find(ch) != name.end() ? name[ch] : ch;
        occ[newName] = occ[newName] + 1;
    }
    
    std::vector<long> result;
    for (auto& pair : occ) {
        result.push_back(pair.second);
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("URW rNB")) == (std::vector<long>({(long)1, (long)1, (long)1, (long)1, (long)1, (long)1, (long)1})));
}
