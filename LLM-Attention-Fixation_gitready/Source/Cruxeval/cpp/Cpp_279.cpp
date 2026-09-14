#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string ans = "";
    while (text != "") {
        size_t pos = text.find_first_of('(');
        std::string x = text.substr(0, pos);
        text = text.substr(pos);
        ans = x + text[0] + ans;
        ans = ans + '|' + text[0] + ans;
        text = text.substr(1);
    }
    return ans;
}
int main() {
    auto candidate = f;
    assert(candidate(("")) == (""));
}
