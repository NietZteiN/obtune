#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string a, std::string b) {
    text = std::regex_replace(text, std::regex(a), b);
    return std::regex_replace(text, std::regex(b), a);
}
int main() {
    auto candidate = f;
    assert(candidate((" vup a zwwo oihee amuwuuw! "), ("a"), ("u")) == (" vap a zwwo oihee amawaaw! "));
}
