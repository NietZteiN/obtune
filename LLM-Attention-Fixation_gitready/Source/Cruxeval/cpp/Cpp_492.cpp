#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string value) {
    std::vector<char> ls(text.begin(), text.end());
    int count = std::count(ls.begin(), ls.end(), value[0]);
    if (count % 2 == 0) {
        ls.erase(std::remove(ls.begin(), ls.end(), value[0]), ls.end());
    } else {
        ls.clear();
    }
    std::string result(ls.begin(), ls.end());
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("abbkebaniuwurzvr"), ("m")) == ("abbkebaniuwurzvr"));
}
