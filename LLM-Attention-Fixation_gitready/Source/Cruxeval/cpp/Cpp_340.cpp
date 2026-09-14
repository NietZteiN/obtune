#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    size_t uppercase_index = text.find('A');
    if (uppercase_index != std::string::npos) {
        return text.substr(0, uppercase_index) + text.substr(text.find('a') + 1);
    } else {
        std::sort(text.begin(), text.end());
        return text;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("E jIkx HtDpV G")) == ("   DEGHIVjkptx"));
}
