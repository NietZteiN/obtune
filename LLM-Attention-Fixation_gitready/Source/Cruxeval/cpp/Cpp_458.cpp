#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string search_chars, std::string replace_chars) {
    std::map<char, char> trans_table;
    for(size_t i = 0; i < search_chars.size(); ++i) {
        trans_table[search_chars[i]] = replace_chars[i];
    }
    std::string result;
    for(char c : text) {
        if(trans_table.find(c) != trans_table.end()) {
            result += trans_table[c];
        } else {
            result += c;
        }
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("mmm34mIm"), ("mm3"), (",po")) == ("pppo4pIp"));
}
