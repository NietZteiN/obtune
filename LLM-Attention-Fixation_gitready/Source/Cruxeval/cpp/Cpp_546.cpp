#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string speaker) {
    while(text.find(speaker) == 0) {
        text = text.substr(speaker.length());
    }
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("[CHARRUNNERS]Do you know who the other was? [NEGMENDS]"), ("[CHARRUNNERS]")) == ("Do you know who the other was? [NEGMENDS]"));
}
