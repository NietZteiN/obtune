#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string chars) {
    if (!chars.empty()) {
        text.erase(text.find_last_not_of(chars) + 1);
    } else {
        text.erase(text.find_last_not_of(' ') + 1);
    }
    if (text.empty()) {
        return "-";
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("new-medium-performing-application - XQuery 2.2"), ("0123456789-")) == ("new-medium-performing-application - XQuery 2."));
}
