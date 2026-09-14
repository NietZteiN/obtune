#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    if (std::all_of(text.begin(), text.end(), ::isupper)) {
        return "ALL UPPERCASE";
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("Hello Is It MyClass")) == ("Hello Is It MyClass"));
}
