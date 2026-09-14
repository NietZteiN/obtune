#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long tab_size) {
    size_t pos = text.find('\t');
    while (pos != std::string::npos) {
        text.replace(pos, 1, std::string(tab_size, ' '));
        pos = text.find('\t', pos + tab_size);
    }
    
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("a"), (100)) == ("a"));
}
