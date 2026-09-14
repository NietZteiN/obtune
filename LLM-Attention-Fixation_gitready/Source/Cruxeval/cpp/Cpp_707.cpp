#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long position) {
    size_t length = text.length();
    int index = position % (length + 1);
    if (position < 0 || index < 0) {
        index = -1;
    }
    std::vector<char> new_text(text.begin(), text.end());
    new_text.erase(new_text.begin() + index);
    return std::string(new_text.begin(), new_text.end());
}
int main() {
    auto candidate = f;
    assert(candidate(("undbs l"), (1)) == ("udbs l"));
}
