#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text, std::string letter) {
    std::unordered_map<char, long> counts;
    for (char c : text) {
        counts[c]++;
    }
    return counts[letter[0]];
}
int main() {
    auto candidate = f;
    assert(candidate(("za1fd1as8f7afasdfam97adfa"), ("7")) == (2));
}
