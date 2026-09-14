#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string text) {
    std::vector<char> valid_chars = {'-', '_', '+', '.', '/', ' '};
    std::transform(text.begin(), text.end(), text.begin(), ::toupper);
    for (char& c : text) {
        if (!isalnum(c) && std::find(valid_chars.begin(), valid_chars.end(), c) == valid_chars.end()) {
            return false;
        }
    }
    return true;
}
int main() {
    auto candidate = f;
    assert(candidate(("9.twCpTf.H7 HPeaQ^ C7I6U,C:YtW")) == (false));
}
