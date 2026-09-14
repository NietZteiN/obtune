#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    for(int i = text.size() - 1; i >= 0; i--) {
        if(isspace(text[i])) {
            text.replace(i, 1, "&nbsp;");
        }
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("   ")) == ("&nbsp;&nbsp;&nbsp;"));
}
