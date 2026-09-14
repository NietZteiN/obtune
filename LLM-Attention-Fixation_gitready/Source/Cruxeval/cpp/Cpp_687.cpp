#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::vector<char> t(text.begin(), text.end());
    t.erase(t.begin() + t.size() / 2);
    std::transform(text.begin(), text.end(), text.begin(), ::tolower);
    std::string result;
    for(char c : t) {
        result += c;
        result += ":";
    }
    result += text;
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("Rjug nzufE")) == ("R:j:u:g: :z:u:f:E:rjug nzufe"));
}
