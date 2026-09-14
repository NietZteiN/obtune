#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string new_text = text;
    for (char i : "+") {
        size_t pos = new_text.find(i);
        if (pos != std::string::npos) {
            new_text.erase(pos, 1);
        }
    }
    return new_text;
}
int main() {
    auto candidate = f;
    assert(candidate(("hbtofdeiequ")) == ("hbtofdeiequ"));
}
