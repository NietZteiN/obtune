#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> container, long cron) {
    std::vector<long> pref;
    auto it = std::find(container.begin(), container.end(), cron);
    if (it != container.end()) {
        pref.assign(container.begin(), it);
        it++;
        container.erase(container.begin(), it);
    }
    return container;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>()), (2)) == (std::vector<long>()));
}
