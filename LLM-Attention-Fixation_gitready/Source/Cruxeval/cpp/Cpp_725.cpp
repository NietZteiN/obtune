#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text) {
    std::vector<std::string> result_list = {"3", "3", "3", "3"};
    if (!result_list.empty()) {
        result_list.clear();
    }
    return text.size();
}
int main() {
    auto candidate = f;
    assert(candidate(("mrq7y")) == (5));
}
