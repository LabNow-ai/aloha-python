ARG BASE_NAMESPACE="quay.io"
ARG BASE_IMG="labnow/node:latest"

# this var PROFILE_LOCALIZE will be used in /opt/utils/script-localize.sh
ARG PROFILE_LOCALIZE="aliyun-pub"

FROM ${BASE_NAMESPACE:+$BASE_NAMESPACE/}${BASE_IMG} AS dev

ARG PROFILE_LOCALIZE

COPY src/pyproject.toml /tmp/

USER root
RUN set -eux && pwd && ls -alh \
 && source /opt/utils/script-localize.sh ${PROFILE_LOCALIZE} \
 ## ----------- handle frontend matters -----------
 && npm install -g pnpm \
 ## ----------- handle backend matters ------------
 && pip install -U --no-cache-dir pip jupyterlab uv \
 && uv pip install --system -r /tmp/pyproject.toml \
 ## ----------- install db client to connect db via terminal ------------
 && source /opt/utils/script-setup-db-clients.sh && setup_postgresql_client 18 \
 ## ----------- ai for coding tools in dev env ------------
 && npm install -g @anthropic-ai/claude-code --allow-scripts=@anthropic-ai/claude-code \
 ## && npm install -g @openai/codex \
 ## && npm install -g @github/copilot \
 ## && curl -fsSL https://antigravity.google/cli/install.sh | bash \
 ## && mkdir -pv /opt/bin && mv ~/.local/bin/agy /opt/bin/ && ln -sf /opt/bin/agy /usr/local/bin/ \
 ## ----------- clean up -----------
 && source /opt/utils/script-utils.sh && list_installed_packages && install__clean

CMD ["tail", "-f", "/dev/null"]
