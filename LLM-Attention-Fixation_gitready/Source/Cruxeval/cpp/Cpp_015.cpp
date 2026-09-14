#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string wrong, std::string right) {
    std::string new_text = text;
    size_t pos = 0;
    while ((pos = new_text.find(wrong, pos)) != std::string::npos) {
        new_text.replace(pos, wrong.length(), right);
        pos += right.length();
    }
    
    std::transform(new_text.begin(), new_text.end(), new_text.begin(), ::toupper);
    
    return new_text;
}
int main() {
    auto candidate = f;
    assert(candidate(("zn kgd jw lnt"), ("h"), ("u")) == ("ZN KGD JW LNT"));
}
