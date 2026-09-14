#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::istringstream iss(text);
    std::vector<std::string> my_list;
    std::string word;
    while(iss >> word) {
        my_list.push_back(word);
    }
    std::sort(my_list.rbegin(), my_list.rend());
    return std::accumulate(my_list.begin(), my_list.end(), std::string(""), [](const std::string& a, const std::string& b) {
        return a + (a.length() > 0 ? " " : "") + b;
    });
}
int main() {
    auto candidate = f;
    assert(candidate(("a loved")) == ("loved a"));
}
