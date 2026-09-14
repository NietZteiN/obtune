#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long tabstop) {
    text = std::regex_replace(text, std::regex("\n"), "_____");
    text = std::regex_replace(text, std::regex("\t"), std::string(tabstop, ' '));
    text = std::regex_replace(text, std::regex("_____"), "\n");
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("odes	code	well"), (2)) == ("odes  code  well"));
}
