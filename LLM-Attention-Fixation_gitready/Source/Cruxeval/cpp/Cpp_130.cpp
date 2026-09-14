#include<assert.h>
#include<bits/stdc++.h>

std::string f(std::map<std::string,long> m) {
    std::vector<std::pair<std::string, long>> items(m.begin(), m.end());
    for (int i = items.size() - 2; i >= 0; --i) {
        auto tmp = items[i];
        items[i] = items[i+1];
        items[i+1] = tmp;
    }
    std::stringstream ss;
    if (items.size() % 2 == 0) {
        ss << items[items.size() - 1].first << "=" << items[items.size() - 2].first;
    } else {
        ss << items[items.size() - 2].first << "=" << items[items.size() - 1].first;
    }
    return ss.str();
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,long>({{"l", 4}, {"h", 6}, {"o", 9}}))) == ("h=l"));
}
