import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

const RECONNECT_DELAY_MS = 3000;

@Injectable({ providedIn: 'root' })
export class WebSocketService {
  connect(url: string): Observable<unknown> {
    return new Observable<unknown>((subscriber) => {
      let socket: WebSocket | null = null;
      let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
      let closed = false;

      const connect = (): void => {
        if (closed) return;

        const currentSocket = new WebSocket(url);
        socket = currentSocket;

        currentSocket.onmessage = (event: MessageEvent) => {
          if (typeof event.data !== 'string') {
            console.warn('[WebSocket] Received a non-text message:', event.data);
            return;
          }

          try {
            const message: unknown = JSON.parse(event.data);
            subscriber.next(message);
          } catch {
            console.warn('[WebSocket] Failed to parse message:', event.data);
          }
        };

        currentSocket.onclose = () => {
          if (!closed) {
            reconnectTimer = setTimeout(connect, RECONNECT_DELAY_MS);
          }
        };

        currentSocket.onerror = () => currentSocket.close();
      };

      connect();

      return () => {
        closed = true;
        if (reconnectTimer !== null) clearTimeout(reconnectTimer);
        socket?.close();
      };
    });
  }
}
