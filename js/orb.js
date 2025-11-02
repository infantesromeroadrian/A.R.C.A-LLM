/* ===== RENDERIZADO DEL ANILLO EXTERIOR - ESTELA SOLAR PROFESIONAL ===== */

// Dibujar anillo ondulado ultra mejorado con múltiples capas profesionales
function dibujarOrbePrincipal(animationTime, intensity) {
    ctx.save();
    ctx.translate(centerX, centerY);
    
    // Radio base del anillo - optimizado y más preciso
    const baseRadius = orbRadius * 5.6;
    const ringWidthBase = orbRadius * 5.2;
    const ringWidth = ringWidthBase * (0.3 + intensity * 0.25);
    const enhancedIntensity = Math.pow(intensity, 0.85); // Curva de respuesta más suave
    
    // Crear múltiples rutas para diferentes capas de profundidad
    const paths = {
        outer: [],
        middle: [],
        inner: []
    };
    
    // Generar ondas complejas con múltiples frecuencias
    for (let i = 0; i <= totalPoints; i++) {
        const point = orbPoints[i % totalPoints];
        
        // Sistema de ondas mejorado con múltiples armónicos
        const minAmp = 2.5;
        const maxAmp = point.waveSize * 0.6;
        const currentAmp = minAmp + (maxAmp - minAmp) * enhancedIntensity;
        
        // Ondas primarias (rápidas)
        const wave1 = Math.sin(animationTime * point.speed * 4.2 + point.offset) * currentAmp;
        // Ondas secundarias (medias)
        const wave2 = Math.sin(animationTime * point.speed * 3.1 + point.offset * 1.3) * currentAmp * 0.6;
        // Ondas terciarias (lentas) para suavidad
        const wave3 = Math.sin(animationTime * point.speed * 1.8 + point.offset * 0.7) * currentAmp * 0.3;
        const audioWave = wave1 + wave2 + wave3;
        
        // Pulso orgánico con múltiples frecuencias
        const pulse1 = Math.sin(animationTime * 2.6) * 5 * enhancedIntensity;
        const pulse2 = Math.sin(animationTime * 1.4) * 2.5 * (1 - enhancedIntensity * 0.5);
        const pulse3 = Math.sin(animationTime * 0.8) * 1.5 * enhancedIntensity;
        const pulse = pulse1 + pulse2 + pulse3;

        const radius = baseRadius + audioWave + pulse;
        
        // Generar puntos para tres capas (anillo más grueso visualmente)
        paths.outer.push({
            x: Math.cos(point.angle) * (radius + ringWidth * 0.15),
            y: Math.sin(point.angle) * (radius + ringWidth * 0.15)
        });
        paths.middle.push({
            x: Math.cos(point.angle) * radius,
            y: Math.sin(point.angle) * radius
        });
        paths.inner.push({
            x: Math.cos(point.angle) * (radius - ringWidth * 0.15),
            y: Math.sin(point.angle) * (radius - ringWidth * 0.15)
        });
    }
    
    // === CAPA 1: HALO EXTERIOR ULTRA SUAVE ===
    ctx.beginPath();
    paths.outer.forEach((p, i) => {
        if (i === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
    });
    ctx.closePath();
    
    const haloGradient = ctx.createRadialGradient(0, 0, baseRadius * 0.3, 0, 0, baseRadius * 1.5);
    haloGradient.addColorStop(0, `rgba(100, 220, 255, ${0.08 + enhancedIntensity * 0.12})`);
    haloGradient.addColorStop(0.5, `rgba(80, 200, 255, ${0.12 + enhancedIntensity * 0.18})`);
    haloGradient.addColorStop(1, `rgba(0, 150, 255, ${0.04 + enhancedIntensity * 0.08})`);
    
    ctx.fillStyle = haloGradient;
    ctx.globalCompositeOperation = 'lighter';
    ctx.shadowBlur = 120 + enhancedIntensity * 80;
    ctx.shadowColor = `rgba(100, 230, 255, ${0.6 + enhancedIntensity * 0.3})`;
    ctx.fill();
    
    // === CAPA 2: BORDE PRINCIPAL CON GRADIENTE PERFECTO ===
    ctx.beginPath();
    paths.middle.forEach((p, i) => {
        if (i === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
    });
    ctx.closePath();
    
    const mainGradient = ctx.createRadialGradient(0, 0, baseRadius - ringWidth * 0.5, 0, 0, baseRadius + ringWidth * 0.5);
    mainGradient.addColorStop(0, `rgba(0, 80, 160, ${0.32 + enhancedIntensity * 0.28})`);
    mainGradient.addColorStop(0.3, `rgba(0, 120, 220, ${0.65 + enhancedIntensity * 0.2})`);
    mainGradient.addColorStop(0.5, `rgba(0, 170, 255, ${0.85 + enhancedIntensity * 0.1})`);
    mainGradient.addColorStop(0.7, `rgba(100, 240, 255, ${0.95 + enhancedIntensity * 0.05})`);
    mainGradient.addColorStop(0.85, `rgba(0, 170, 255, ${0.75 + enhancedIntensity * 0.15})`);
    mainGradient.addColorStop(1, `rgba(0, 100, 180, ${0.25 + enhancedIntensity * 0.2})`);
    
    ctx.strokeStyle = mainGradient;
    ctx.lineWidth = ringWidth * 0.4;
    ctx.globalCompositeOperation = 'source-over';
    ctx.shadowBlur = 45 + enhancedIntensity * 55;
    ctx.shadowColor = `rgba(0, 220, 255, ${0.85 + enhancedIntensity * 0.15})`;
    ctx.stroke();
    
    // === CAPA 3: BRILLO INTERNO ADITIVO ===
    ctx.beginPath();
    paths.middle.forEach((p, i) => {
        if (i === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
    });
    ctx.closePath();
    
    ctx.strokeStyle = `rgba(150, 240, 255, ${0.22 + enhancedIntensity * 0.28})`;
    ctx.lineWidth = ringWidth * 0.25;
    ctx.globalCompositeOperation = 'lighter';
    ctx.shadowBlur = 90 + enhancedIntensity * 70;
    ctx.shadowColor = `rgba(150, 240, 255, ${0.85 + enhancedIntensity * 0.15})`;
    ctx.stroke();
    
    // === CAPA 4: FILO INTERNO PRECISO ===
    ctx.beginPath();
    paths.inner.forEach((p, i) => {
        if (i === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
    });
    ctx.closePath();
    
    const innerGradient = ctx.createLinearGradient(-baseRadius, 0, baseRadius, 0);
    innerGradient.addColorStop(0, `rgba(0, 140, 230, ${0.4 + enhancedIntensity * 0.3})`);
    innerGradient.addColorStop(0.5, `rgba(0, 180, 255, ${0.5 + enhancedIntensity * 0.35})`);
    innerGradient.addColorStop(1, `rgba(0, 140, 230, ${0.4 + enhancedIntensity * 0.3})`);
    
    ctx.strokeStyle = innerGradient;
    ctx.lineWidth = Math.max(1.5, ringWidth * 0.12);
    ctx.globalCompositeOperation = 'source-over';
    ctx.shadowBlur = 15 + enhancedIntensity * 20;
    ctx.shadowColor = `rgba(0, 180, 255, ${0.65 + enhancedIntensity * 0.25})`;
    ctx.stroke();
    
    // === CAPA 5: PUNTOS DE ENERGÍA BRILLANTES (adicional) ===
    if (enhancedIntensity > 0.3) {
        ctx.globalCompositeOperation = 'lighter';
        for (let i = 0; i < totalPoints; i += Math.floor(totalPoints / 12)) {
            const point = orbPoints[i];
            const radius = baseRadius + Math.sin(animationTime * point.speed * 4 + point.offset) * (point.waveSize * 0.4 * enhancedIntensity);
            const x = Math.cos(point.angle) * radius;
            const y = Math.sin(point.angle) * radius;
            
            const sparkleIntensity = 0.3 + enhancedIntensity * 0.7;
            ctx.fillStyle = `rgba(200, 250, 255, ${sparkleIntensity})`;
            ctx.shadowBlur = 25 + enhancedIntensity * 35;
            ctx.shadowColor = `rgba(200, 250, 255, 0.9)`;
            ctx.beginPath();
            ctx.arc(x, y, 2 + enhancedIntensity * 2, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    ctx.restore();
}
