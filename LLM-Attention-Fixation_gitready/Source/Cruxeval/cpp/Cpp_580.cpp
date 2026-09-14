#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::string text, std::string char_) {
    std::vector<long> a;
    std::string new_text = text;
    while (new_text.find(char_) != std::string::npos) {
        a.push_back(new_text.find(char_));
        new_text.replace(new_text.find(char_), 1, "");
    }
    return a;
}
int main() {
    auto candidate = f;
    assert(candidate(("rvr"), ("r")) == (std::vector<long>({(long)0, (long)1})));
}
