#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string value) {
    int padding = value.size() - text.size();
    if (padding > 0) {
        text.append(padding, '?');
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("!?"), ("")) == ("!?"));
}
