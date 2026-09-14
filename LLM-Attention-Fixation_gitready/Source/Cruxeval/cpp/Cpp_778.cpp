#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string prefix, std::string text) {
    if (text.find(prefix) == 0) {
        return text;
    } else {
        return prefix + text;
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("mjs"), ("mjqwmjsqjwisojqwiso")) == ("mjsmjqwmjsqjwisojqwiso"));
}
