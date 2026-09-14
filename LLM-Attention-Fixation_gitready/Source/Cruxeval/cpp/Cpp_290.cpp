#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string prefix) {
    if (text.find(prefix) == 0) {
        return text.substr(prefix.length());
    } else if (text.find(prefix) != std::string::npos) {
        size_t pos = text.find(prefix);
        return text.erase(pos, prefix.length()).c_str();
    } else {
        std::transform(text.begin(), text.end(), text.begin(), ::toupper);
        return text;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("abixaaaily"), ("al")) == ("ABIXAAAILY"));
}
