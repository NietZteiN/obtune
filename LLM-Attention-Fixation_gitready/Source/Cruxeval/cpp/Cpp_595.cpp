#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string prefix) {
    if (text.find(prefix) == 0) {
        text = text.substr(prefix.length());
    }
    text[0] = toupper(text[0]);
    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("qdhstudentamxupuihbuztn"), ("jdm")) == ("Qdhstudentamxupuihbuztn"));
}
