#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string prefix) {
    int prefix_length = prefix.size();
    if (text.substr(0, prefix_length) == prefix) {
        return text.substr(prefix_length / 2,prefix_length % 2);
    } else {
        return text;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("happy"), ("ha")) == (""));
}
