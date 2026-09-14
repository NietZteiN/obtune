#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string strip_chars) {
    std::reverse(text.begin(), text.end());
    size_t pos = text.find_last_not_of(strip_chars);
    if(pos != std::string::npos)
        text.erase(pos + 1);
    pos = text.find_first_not_of(strip_chars);
    if(pos != std::string::npos)
        text.erase(0, pos);
    std::reverse(text.begin(), text.end());
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("tcmfsmj"), ("cfj")) == ("tcmfsm"));
}
